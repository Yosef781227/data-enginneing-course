// OCR every page of a PDF with macOS Vision. Usage: swiftc -O ocr_pdf.swift -o ocr_pdf && ./ocr_pdf in.pdf out.txt
import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count == 3, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("usage: ocr_pdf in.pdf out.txt\n".data(using: .utf8)!)
    exit(1)
}

var out = ""
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.0
    let size = NSSize(width: bounds.width * scale, height: bounds.height * scale)
    let image = NSImage(size: size)
    image.lockFocus()
    if let ctx = NSGraphicsContext.current?.cgContext {
        ctx.setFillColor(NSColor.white.cgColor)
        ctx.fill(CGRect(origin: .zero, size: size))
        ctx.scaleBy(x: scale, y: scale)
        page.draw(with: .mediaBox, to: ctx)
    }
    image.unlockFocus()
    var text = ""
    if let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let req = VNRecognizeTextRequest()
        req.recognitionLevel = .accurate
        req.usesLanguageCorrection = true
        try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
        let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
        text = lines.joined(separator: "\n")
    }
    out += "=== Slide \(i + 1) ===\n\(text)\n\n"
}
try! out.write(toFile: args[2], atomically: true, encoding: .utf8)
print("\(args[2]): \(doc.pageCount) pages")
