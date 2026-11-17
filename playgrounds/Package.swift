// swift-tools-version: 5.8
// Projet Swift Playgrounds (iPad) : l'appli Repère embarquée, sans page web en ligne.
import PackageDescription
import AppleProductTypes

let package = Package(
    name: "Repère",
    platforms: [
        .iOS("16.0")
    ],
    products: [
        .iOSApplication(
            name: "Repère",
            targets: ["AppModule"],
            bundleIdentifier: "com.luxhuache.repere",
            displayVersion: "1.0",
            bundleVersion: "1",
            appIcon: .placeholder(icon: .map),
            accentColor: .presetColor(.green),
            supportedDeviceFamilies: [
                .pad
            ],
            supportedInterfaceOrientations: [
                .landscapeRight,
                .landscapeLeft
            ],
            capabilities: [
                .locationWhenInUse(purposeString: "Repère utilise ta position pour suivre le train sur la fiche (PK, limites, profil).")
            ]
        )
    ],
    targets: [
        .executableTarget(
            name: "AppModule",
            path: ".",
            resources: [
                .copy("Resources/www.pack")
            ]
        )
    ]
)
