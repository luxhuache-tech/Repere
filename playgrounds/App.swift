// Repère — appli iPad personnelle, lancée depuis Swift Playgrounds.
// Toute l'appli (page, bibliothèques, données) est dans Resources/www.pack et servie par le schéma repere://app.
// Le GPS vient de l'iPad (CoreLocation) et est transmis à la page ; l'écran reste allumé.
import SwiftUI
import UIKit
import WebKit
import CoreLocation
import UniformTypeIdentifiers

@main
struct RepereApp: App {
    var body: some Scene {
        WindowGroup {
            WebHost()
                .ignoresSafeArea()
                .statusBarHidden(true)
                .persistentSystemOverlays(.hidden)
        }
    }
}

struct WebHost: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> WebVC { WebVC() }
    func updateUIViewController(_ vc: WebVC, context: Context) {}
}

/// Archive www.pack : 8 octets (taille de l'index, petit-boutiste), index JSON {chemin: [début, longueur]}, puis les fichiers.
final class Pack {
    static let shared = Pack()
    private var data = Data()
    private var index: [String: [Int]] = [:]
    private var base = 0
    init() {
        // Swift Playgrounds range les ressources dans le paquet principal ou dans un paquet annexe : on cherche partout.
        var url = Bundle.main.url(forResource: "www", withExtension: "pack")
        if url == nil {
            for b in Bundle.allBundles + Bundle.allFrameworks {
                if let u = b.url(forResource: "www", withExtension: "pack") { url = u; break }
            }
        }
        if url == nil, let res = Bundle.main.resourceURL,
           let e = FileManager.default.enumerator(at: res, includingPropertiesForKeys: nil) {
            for case let u as URL in e where u.lastPathComponent == "www.pack" { url = u; break }
        }
        guard let url, let d = try? Data(contentsOf: url, options: .mappedIfSafe), d.count > 8 else { return }
        var n: UInt64 = 0
        for i in 0..<8 { n |= UInt64(d[d.startIndex + i]) << (8 * UInt64(i)) }
        let head = d.subdata(in: (d.startIndex + 8)..<(d.startIndex + 8 + Int(n)))
        index = (try? JSONSerialization.jsonObject(with: head) as? [String: [Int]]) ?? [:]
        base = 8 + Int(n)
        data = d
    }
    func file(_ path: String) -> Data? {
        guard let e = index[path], e.count == 2 else { return nil }
        let a = data.startIndex + base + e[0]
        return data.subdata(in: a..<(a + e[1]))
    }
}

/// Sert les fichiers embarqués.
final class Local: NSObject, WKURLSchemeHandler {
    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else { return }
        var path = url.path
        if path.isEmpty || path == "/" { path = "/index.html" }
        let rel = String(path.dropFirst()).removingPercentEncoding ?? String(path.dropFirst())
        guard let body = Pack.shared.file(rel) else {
            task.didReceive(HTTPURLResponse(url: url, statusCode: 404, httpVersion: "HTTP/1.1", headerFields: [:])!)
            task.didFinish()
            return
        }
        let ext = (rel as NSString).pathExtension
        let mime = UTType(filenameExtension: ext)?.preferredMIMEType ?? "application/octet-stream"
        task.didReceive(HTTPURLResponse(url: url, statusCode: 200, httpVersion: "HTTP/1.1",
                                        headerFields: ["Content-Type": mime, "Content-Length": "\(body.count)", "Cache-Control": "no-cache"])!)
        task.didReceive(body)
        task.didFinish()
    }
    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

final class WebVC: UIViewController, WKUIDelegate, WKScriptMessageHandler, CLLocationManagerDelegate {
    var web: WKWebView!
    let loc = CLLocationManager()

    // Remplace navigator.geolocation par la position de l'iPad.
    static let geoShim = """
    (function(){
      var W={},n=0,last=null;
      window.__repereGeo=function(p){last=p;for(var k in W){try{W[k].ok(p)}catch(e){}}};
      window.__repereGeoErr=function(c,m){for(var k in W){try{W[k].ko&&W[k].ko({code:c,message:m})}catch(e){}}};
      var g={watchPosition:function(ok,ko){var id=++n;W[id]={ok:ok,ko:ko};webkit.messageHandlers.geo.postMessage('start');if(last)setTimeout(function(){ok(last)},0);return id},
             clearWatch:function(id){delete W[id];if(!Object.keys(W).length)webkit.messageHandlers.geo.postMessage('stop')},
             getCurrentPosition:function(ok,ko){if(last){ok(last);return}var id=g.watchPosition(function(p){g.clearWatch(id);ok(p)},ko)}};
      try{Object.defineProperty(navigator,'geolocation',{value:g,configurable:true})}catch(e){}
    })();
    """

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 0.08, green: 0.09, blue: 0.11, alpha: 1)
        let cfg = WKWebViewConfiguration()
        cfg.setURLSchemeHandler(Local(), forURLScheme: "repere")
        cfg.websiteDataStore = .default()
        let uc = WKUserContentController()
        uc.addUserScript(WKUserScript(source: WebVC.geoShim, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        uc.add(self, name: "geo")
        cfg.userContentController = uc
        web = WKWebView(frame: view.bounds, configuration: cfg)
        web.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        web.uiDelegate = self
        web.isOpaque = false
        web.backgroundColor = view.backgroundColor
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.scrollView.bounces = false
        view.addSubview(web)
        loc.delegate = self
        loc.desiredAccuracy = kCLLocationAccuracyBestForNavigation
        loc.activityType = .otherNavigation
        loc.distanceFilter = kCLDistanceFilterNone
        UIApplication.shared.isIdleTimerDisabled = true
        web.load(URLRequest(url: URL(string: "repere://app/index.html")!))
    }

    // GPS
    func userContentController(_ c: WKUserContentController, didReceive m: WKScriptMessage) {
        guard let s = m.body as? String else { return }
        if s == "start" {
            if loc.authorizationStatus == .notDetermined { loc.requestWhenInUseAuthorization() }
            loc.startUpdatingLocation()
        } else if s == "stop" {
            loc.stopUpdatingLocation()
        }
    }
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        for l in locations {
            let sp = l.speed >= 0 ? "\(l.speed)" : "null"
            let hd = l.course >= 0 ? "\(l.course)" : "null"
            let js = "window.__repereGeo&&window.__repereGeo({coords:{latitude:\(l.coordinate.latitude),longitude:\(l.coordinate.longitude),accuracy:\(l.horizontalAccuracy),altitude:\(l.altitude),altitudeAccuracy:\(l.verticalAccuracy),speed:\(sp),heading:\(hd)},timestamp:\(Int64(l.timestamp.timeIntervalSince1970 * 1000))})"
            web.evaluateJavaScript(js)
        }
    }
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        let denied = (error as? CLError)?.code == .denied
        web.evaluateJavaScript("window.__repereGeoErr&&window.__repereGeoErr(\(denied ? 1 : 2),'\(denied ? "Localisation refusée" : "Position indisponible")')")
    }
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        if manager.authorizationStatus == .authorizedWhenInUse || manager.authorizationStatus == .authorizedAlways {
            manager.startUpdatingLocation()
        }
    }

    // Boîtes de dialogue de la page
    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage msg: String, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: msg, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in done() })
        present(a, animated: true)
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage msg: String, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping (Bool) -> Void) {
        let a = UIAlertController(title: nil, message: msg, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "Annuler", style: .cancel) { _ in done(false) })
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in done(true) })
        present(a, animated: true)
    }
    func webView(_ w: WKWebView, runJavaScriptTextInputPanelWithPrompt p: String, defaultText t: String?, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping (String?) -> Void) {
        let a = UIAlertController(title: nil, message: p, preferredStyle: .alert)
        a.addTextField { $0.text = t }
        a.addAction(UIAlertAction(title: "Annuler", style: .cancel) { _ in done(nil) })
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in done(a.textFields?.first?.text) })
        present(a, animated: true)
    }
}
