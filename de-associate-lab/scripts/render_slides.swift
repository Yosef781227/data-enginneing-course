// Render each PDF page to a JPEG. Usage: render_slides in.pdf outdir [width]
import Foundation
import PDFKit
import AppKit
let a = CommandLine.arguments
guard a.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else { print("usage"); exit(1) }
let width = a.count > 3 ? CGFloat(Double(a[3]) ?? 1100) : 1100
try? FileManager.default.createDirectory(atPath: a[2], withIntermediateDirectories: true)
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let b = page.bounds(for: .mediaBox)
    let scale = width / b.width
    let size = NSSize(width: b.width * scale, height: b.height * scale)
    let img = NSImage(size: size)
    img.lockFocus()
    if let ctx = NSGraphicsContext.current?.cgContext {
        ctx.setFillColor(NSColor.white.cgColor); ctx.fill(CGRect(origin: .zero, size: size))
        ctx.scaleBy(x: scale, y: scale); page.draw(with: .mediaBox, to: ctx)
    }
    img.unlockFocus()
    if let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
       let jpg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.72]) {
        try? jpg.write(to: URL(fileURLWithPath: "\(a[2])/\(i + 1).jpg"))
    }
}
print("\(a[2]): \(doc.pageCount) slides")
