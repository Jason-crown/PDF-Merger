"""PDF Merger — combine multiple PDFs into one.

Run with no arguments to open the GUI:
    python pdf_merger.py

Or use the command line:
    python pdf_merger.py -o merged.pdf a.pdf b.pdf:1-3,5 c.pdf
    (append ":<pages>" to a file to pick pages, 1-based, e.g. "file.pdf:2-4,7")
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


# ---------------------------------------------------------------- core logic

def parse_pages(spec: str, page_count: int) -> list[int]:
    """Turn '1-3,5,8-' into zero-based page indices. Empty spec = all pages."""
    spec = spec.strip()
    if not spec:
        return list(range(page_count))
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s) if start_s.strip() else 1
            end = int(end_s) if end_s.strip() else page_count
        else:
            start = end = int(part)
        if not (1 <= start <= page_count and 1 <= end <= page_count):
            raise ValueError(f"Page range '{part}' is outside 1-{page_count}")
        step = 1 if end >= start else -1
        pages.extend(range(start - 1, end - 1 + step, step))
    return pages


def merge_pdfs(items: list[tuple[str, str]], output: str) -> int:
    """Merge (path, page_spec) items into output. Returns total pages written."""
    if not items:
        raise ValueError("No input files given")
    writer = PdfWriter()
    for path, spec in items:
        reader = PdfReader(path)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError(f"'{Path(path).name}' is password-protected")
        for i in parse_pages(spec, len(reader.pages)):
            writer.add_page(reader.pages[i])
    total = len(writer.pages)
    with open(output, "wb") as f:
        writer.write(f)
    return total


# ---------------------------------------------------------------------- CLI

def split_arg(arg: str) -> tuple[str, str]:
    """'file.pdf:1-3' -> ('file.pdf', '1-3'). Handles Windows drive letters."""
    head, sep, tail = arg.rpartition(":")
    if sep and head and not tail.startswith(("\\", "/")) and Path(head).suffix.lower() == ".pdf":
        return head, tail
    return arg, ""


def run_cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Merge PDF files.")
    p.add_argument("inputs", nargs="+", help="PDF files, optionally 'file.pdf:1-3,5'")
    p.add_argument("-o", "--output", default="merged.pdf", help="output file")
    args = p.parse_args(argv)
    try:
        n = merge_pdfs([split_arg(a) for a in args.inputs], args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {n} pages to {args.output}")
    return 0


# ---------------------------------------------------------------------- GUI

def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk

    root = tk.Tk()
    root.title("PDF Merger")
    root.geometry("720x420")
    root.minsize(520, 300)

    # Each entry: {"path": str, "pages": str, "count": int}
    files: list[dict] = []

    tree = ttk.Treeview(root, columns=("file", "pages", "count"), show="headings", selectmode="extended")
    tree.heading("file", text="File")
    tree.heading("pages", text="Pages to include")
    tree.heading("count", text="Total pages")
    tree.column("file", width=420)
    tree.column("pages", width=140, anchor="center")
    tree.column("count", width=90, anchor="center")

    def refresh(select: list[int] | None = None) -> None:
        tree.delete(*tree.get_children())
        for i, f in enumerate(files):
            tree.insert("", "end", iid=str(i), values=(Path(f["path"]).name, f["pages"] or "all", f["count"]))
        if select:
            tree.selection_set([str(i) for i in select])
        status.set(f"{len(files)} file(s)")

    def selected() -> list[int]:
        return sorted(int(i) for i in tree.selection())

    def add_files() -> None:
        paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for path in paths:
            try:
                count = len(PdfReader(path).pages)
            except Exception as e:
                messagebox.showerror("Can't open file", f"{Path(path).name}:\n{e}")
                continue
            files.append({"path": path, "pages": "", "count": count})
        refresh()

    def remove() -> None:
        for i in reversed(selected()):
            del files[i]
        refresh()

    def move(delta: int) -> None:
        sel = selected()
        if not sel:
            return
        if (delta < 0 and sel[0] == 0) or (delta > 0 and sel[-1] == len(files) - 1):
            return
        order = sel if delta < 0 else list(reversed(sel))
        for i in order:
            files[i], files[i + delta] = files[i + delta], files[i]
        refresh([i + delta for i in sel])

    def set_pages(_event=None) -> None:
        sel = selected()
        if len(sel) != 1:
            return
        f = files[sel[0]]
        spec = simpledialog.askstring("Pages", f"Pages from {Path(f['path']).name} (1-{f['count']}).\n" "e.g. 1-3,5,8-   (blank = all)", initialvalue=f["pages"], parent=root)
        if spec is None:
            return
        try:
            parse_pages(spec, f["count"])
        except ValueError as e:
            messagebox.showerror("Invalid pages", str(e))
            return
        f["pages"] = spec.strip()
        refresh(sel)

    def merge() -> None:
        if not files:
            messagebox.showinfo("Nothing to merge", "Add some PDFs first.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="merged.pdf", filetypes=[("PDF files", "*.pdf")])
        if not out:
            return
        if any(Path(out).resolve() == Path(f["path"]).resolve() for f in files):
            messagebox.showerror("Error", "Output can't be one of the input files.")
            return
        try:
            n = merge_pdfs([(f["path"], f["pages"]) for f in files], out)
        except Exception as e:
            messagebox.showerror("Merge failed", str(e))
            return
        messagebox.showinfo("Done", f"Wrote {n} pages to\n{out}")

    btns = ttk.Frame(root, padding=(8, 8, 8, 0))
    for text, cmd in [("Add PDFs…", add_files), ("Remove", remove), ("Move up", lambda: move(-1)), ("Move down", lambda: move(1)), ("Set pages…", set_pages)]:
        ttk.Button(btns, text=text, command=cmd).pack(side="left", padx=(0, 6))
    ttk.Button(btns, text="Merge →", command=merge).pack(side="right")
    btns.pack(fill="x")

    tree.pack(fill="both", expand=True, padx=8, pady=8)
    tree.bind("<Double-1>", set_pages)
    tree.bind("<Delete>", lambda e: remove())

    status = tk.StringVar(value="0 file(s) — double-click a row to choose pages")
    ttk.Label(root, textvariable=status, padding=(8, 0, 8, 6)).pack(fill="x")

    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(run_cli(sys.argv[1:]))
    run_gui()
