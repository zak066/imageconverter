import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Callable
import threading

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
import config
from converter import convert_files, ImageConverter, SUPPORTED_FORMATS
import version


class ImageConverterGUI:
    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title(f"Image Converter v{version.__version__}")
        self.root.geometry("600x750")
        self.root.resizable(True, True)

        self.config_manager = config.ConfigManager()
        self.selected_path: Optional[Path] = None
        self.image_files: list = []
        self.converting = False
        self.converter: Optional[ImageConverter] = None
        self._results_log = []

        self._setup_ui()
        if DND_AVAILABLE:
            self._setup_drag_drop()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame, text="🖼️ Image Converter", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_folder = ttk.Button(
            button_frame, text="📂 Cartella", command=self._select_folder
        )
        self.btn_folder.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_file = ttk.Button(
            button_frame, text="📄 File", command=self._select_file
        )
        self.btn_file.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_export = ttk.Button(
            button_frame, text="📤 Esporta Config", command=self._export_config
        )
        self.btn_export.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_import = ttk.Button(
            button_frame, text="📥 Importa Config", command=self._import_config
        )
        self.btn_import.pack(side=tk.LEFT)

        drop_frame = ttk.LabelFrame(main_frame, text="Drag & Drop", padding="10")
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.drop_label = ttk.Label(
            drop_frame,
            text="Trascina cartella o file qui",
            background="#f0f0f0",
            relief=tk.SUNKEN,
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)

        options_frame = ttk.LabelFrame(main_frame, text="Opzioni", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.format_var = tk.StringVar(value=self.config_manager.config.output_format)
        for fmt in ["WebP", "AVIF", "Entrambi"]:
            value = fmt.lower() if fmt != "Entrambi" else "both"
            rb = ttk.Radiobutton(
                options_frame, text=fmt, variable=self.format_var, value=value
            )
            rb.pack(side=tk.LEFT, padx=(0, 10))

        self.quality_var = tk.IntVar(value=self.config_manager.config.quality)
        self.quality_label = ttk.Label(
            options_frame, text=f"Qualità: {self.quality_var.get()}%"
        )
        self.quality_label.pack(side=tk.LEFT, padx=(20, 5))

        quality_scale = ttk.Scale(
            options_frame,
            from_=0,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            command=self._on_quality_change,
        )
        quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        output_options = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_options.pack(fill=tk.X, pady=(0, 10))

        self.output_folder_var = tk.StringVar(
            value=self.config_manager.config.output_folder or ""
        )
        ttk.Label(output_options, text="Cartella:").pack(side=tk.LEFT)
        self.output_folder_entry = ttk.Entry(
            output_options, textvariable=self.output_folder_var, width=20
        )
        self.output_folder_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(
            output_options, text="...", command=self._select_output_folder, width=3
        ).pack(side=tk.LEFT)

        self.prefix_var = tk.StringVar(value=self.config_manager.config.prefix)
        ttk.Label(output_options, text=" Prefisso:").pack(side=tk.LEFT, padx=(10, 0))
        self.prefix_entry = ttk.Entry(
            output_options, textvariable=self.prefix_var, width=10
        )
        self.prefix_entry.pack(side=tk.LEFT, padx=(5, 5))

        self.overwrite_var = tk.BooleanVar(value=self.config_manager.config.overwrite)
        ttk.Checkbutton(
            output_options, text="Sovrascrivi", variable=self.overwrite_var
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.skip_existing_var = tk.BooleanVar(
            value=self.config_manager.config.skip_existing
        )
        ttk.Checkbutton(
            output_options, text="Skip esistenti", variable=self.skip_existing_var
        ).pack(side=tk.LEFT, padx=(10, 0))

        resample_frame = ttk.LabelFrame(
            main_frame, text="Ridimensionamento", padding="10"
        )
        resample_frame.pack(fill=tk.X, pady=(0, 10))

        dims = self.config_manager.config.dimensions
        self.dim_entries = {}

        for label, key in [
            ("Large:", "large"),
            ("Medium:", "medium"),
            ("Small:", "small"),
            ("X-Small:", "x_small"),
        ]:
            row = ttk.Frame(resample_frame)
            row.pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(row, text=label, width=8).pack(anchor=tk.W)
            entry = ttk.Entry(row, width=8)
            entry.insert(0, getattr(dims, key))
            entry.pack()
            self.dim_entries[key] = entry

        self.resample_var = tk.StringVar(
            value=self.config_manager.config.resample_method
        )
        ttk.Label(resample_frame, text="Metodo:").pack(side=tk.LEFT, padx=(20, 5))
        resample_combo = ttk.Combobox(
            resample_frame,
            textvariable=self.resample_var,
            values=["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],
            state="readonly",
            width=10,
        )
        resample_combo.pack(side=tk.LEFT, padx=(20, 0))

        sizes_frame = ttk.LabelFrame(
            main_frame, text="Versioni da generare", padding="10"
        )
        sizes_frame.pack(fill=tk.X, pady=(0, 10))

        self.generate_sizes_vars = {}
        default_sizes = self.config_manager.config.generate_sizes
        for size_key in ["original", "large", "medium", "small", "x_small"]:
            var = tk.BooleanVar(value=size_key in default_sizes)
            label = size_key.replace("_", "-").replace("original", "Originale")
            ttk.Checkbutton(sizes_frame, text=label, variable=var).pack(
                side=tk.LEFT, padx=(0, 10)
            )
            self.generate_sizes_vars[size_key] = var

        self.files_label = ttk.Label(
            main_frame, text="File trovati: 0", font=("Arial", 10)
        )
        self.files_label.pack(pady=(0, 5))

        list_frame = ttk.LabelFrame(main_frame, text="File", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.file_listbox = tk.Listbox(list_frame, height=6)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(list_frame, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btn_convert_frame = ttk.Frame(main_frame)
        btn_convert_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_convert = ttk.Button(
            btn_convert_frame, text="🔄 CONVERTI", command=self._start_convert
        )
        self.btn_convert.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_cancel = ttk.Button(
            btn_convert_frame,
            text="⏹ Annulla",
            command=self._cancel_convert,
            state=tk.DISABLED,
        )
        self.btn_cancel.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(main_frame, mode="determinate")
        self.progress.pack(fill=tk.X)

        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=6, state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _setup_drag_drop(self):
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event):
        path = Path(event.data)
        if path.exists():
            self._set_path(path)

    def _select_folder(self):
        path = filedialog.askdirectory(title="Seleziona cartella immagini")
        if path:
            self._set_path(Path(path))

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Seleziona immagine",
            filetypes=[
                ("Immagini", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp *.avif")
            ],
        )
        if path:
            self._set_path(Path(path))

    def _select_output_folder(self):
        path = filedialog.askdirectory(title="Seleziona cartella output")
        if path:
            self.output_folder_var.set(path)

    def _set_path(self, path: Path):
        self.selected_path = path
        if path.is_file():
            self.drop_label.config(text=f"File: {path.name}")
            self.image_files = [path]
        else:
            self.drop_label.config(text=f"Cartella: {path.name}")
            exts = self.config_manager.config.input_extensions
            self.image_files = config.get_image_files(path, exts)

        self.files_label.config(text=f"File trovati: {len(self.image_files)}")
        self.file_listbox.delete(0, tk.END)
        for f in self.image_files:
            self.file_listbox.insert(tk.END, f.name)

    def _get_output_format(self) -> str:
        return self.format_var.get()

    def _get_dimensions(self) -> dict:
        return {key: int(entry.get()) for key, entry in self.dim_entries.items()}

    def _on_quality_change(self, value):
        self.quality_label.config(text=f"Qualità: {int(float(value))}%")

    def _log(self, message: str):
        self._results_log.append(message)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _save_config(self):
        dims = config.Dimensions(**self._get_dimensions())
        output_folder = self.output_folder_var.get() or None

        generate_sizes = [
            key for key, var in self.generate_sizes_vars.items() if var.get()
        ]

        cfg = config.Config(
            dimensions=dims,
            output_format=self.format_var.get(),
            quality=self.quality_var.get(),
            output_folder=output_folder,
            prefix=self.prefix_var.get(),
            overwrite=self.overwrite_var.get(),
            skip_existing=self.skip_existing_var.get(),
            resample_method=self.resample_var.get(),
            generate_sizes=generate_sizes,
        )
        self.config_manager.config = cfg

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            title="Esporta configurazione",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if path:
            self.config_manager.export_config(path)
            messagebox.showinfo("Esportato", f"Config salvata in {path}")

    def _import_config(self):
        path = filedialog.askopenfilename(
            title="Importa configurazione",
            filetypes=[("JSON", "*.json")],
        )
        if path:
            self.config_manager.import_config(path)
            self._reload_config_gui()
            messagebox.showinfo("Importato", "Config importata")

    def _reload_config_gui(self):
        cfg = self.config_manager.config
        self.format_var.set(cfg.output_format)
        self.quality_var.set(cfg.quality)
        self.output_folder_var.set(cfg.output_folder or "")
        self.prefix_var.set(cfg.prefix)
        self.overwrite_var.set(cfg.overwrite)
        self.skip_existing_var.set(cfg.skip_existing)
        self.resample_var.set(cfg.resample_method)
        for key, entry in self.dim_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, getattr(cfg.dimensions, key))
        for key, var in self.generate_sizes_vars.items():
            var.set(key in cfg.generate_sizes)

    def _start_convert(self):
        if not self.selected_path or not self.image_files:
            messagebox.showwarning(
                "Attenzione", "Seleziona una cartella o un file prima"
            )
            return

        if self.converting:
            return

        self.converting = True
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self._results_log = []
        self._log("=== Inizio conversione ===")

        self._save_config()
        cfg = self.config_manager.config
        output_format = self._get_output_format()
        formats = [output_format] if output_format != "both" else ["webp", "avif"]
        generate_sizes = cfg.generate_sizes

        def worker():
            total = len(self.image_files) * len(formats)
            converted = 0
            errors = 0

            for fmt in formats:
                try:
                    results = convert_files(
                        self.selected_path,
                        output_format=fmt,
                        dimensions=cfg.dimensions.__dict__,
                        quality=cfg.quality,
                        output_folder=Path(cfg.output_folder)
                        if cfg.output_folder
                        else None,
                        prefix=cfg.prefix,
                        overwrite=cfg.overwrite,
                        skip_existing=cfg.skip_existing,
                        resample_method=cfg.resample_method,
                        generate_sizes=generate_sizes,
                        progress_callback=lambda v, n, s: self.root.after(
                            0, lambda: self._update_progress(v, n, s)
                        ),
                    )
                    for name, success, msg in results:
                        if success:
                            converted += 1
                            self._log(f"✓ {name}: {msg}")
                        else:
                            errors += 1
                            self._log(f"✗ {name}: {msg}")
                except Exception as e:
                    self._log(f"Errore: {e}")

            self.root.after(0, lambda: self._conversion_complete(converted, errors))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress(self, value, name, msg):
        self.progress["value"] = value
        if name:
            self.status_label.config(text=f"Convertendo: {name}")

    def _conversion_complete(self, converted: int, errors: int):
        self.converting = False
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)
        self.progress["value"] = 100
        self._log(f"=== Completato: {converted} OK, {errors} errori ===")
        self.status_label.config(
            text=f"Completato! {converted} convertiti, {errors} errori"
        )
        messagebox.showinfo(
            "Completato",
            f"Conversione terminata!\n{converted} file OK\n{errors} errori",
        )

    def _cancel_convert(self):
        if self.converter:
            self.converter.cancel()
        self._log("=== Conversione annullata ===")
        self._conversion_complete(0, 0)

    def run(self):
        self.root.mainloop()


def main():
    app = ImageConverterGUI()
    app.run()


if __name__ == "__main__":
    main()
