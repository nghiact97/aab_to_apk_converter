"""
AAB to APK Converter - Windows Desktop Application
Converts Android App Bundle (.aab) to APK using bundletool.
Supports optional keystore signing.
"""

import os
import sys
import subprocess
import threading
import zipfile
import shutil
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime


def get_bundletool_path():
    """Get bundletool.jar path - checks bundled (PyInstaller) first, then local."""
    if getattr(sys, '_MEIPASS', None):
        # PyInstaller bundled
        path = os.path.join(sys._MEIPASS, 'bundletool.jar')
        if os.path.exists(path):
            return path
    # Local file
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bundletool.jar')
    if os.path.exists(path):
        return path
    return None


def check_java():
    """Check if Java is installed. Returns (ok, version_string)."""
    try:
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        # java -version outputs to stderr
        version_info = result.stderr.strip() or result.stdout.strip()
        return True, version_info.split('\n')[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, None


class AABConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window config
        self.title("AAB to APK Converter")
        self.geometry("720x780")
        self.minsize(650, 700)
        self.resizable(True, True)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.aab_path = ctk.StringVar()
        self.keystore_path = ctk.StringVar()
        self.ks_pass = ctk.StringVar()
        self.key_alias = ctk.StringVar()
        self.key_pass = ctk.StringVar()
        self.use_keystore = ctk.BooleanVar(value=False)
        self.converting = False

        self._build_ui()
        self._check_dependencies()

    def _build_ui(self):
        """Build the full UI."""
        # Main scrollable container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Header ──
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header_frame, text="🔄 AAB to APK Converter",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame, text="Convert Android App Bundle to APK with optional keystore signing",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(anchor="w", pady=(2, 0))

        # ── AAB File Section ──
        aab_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        aab_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            aab_frame, text="📁 AAB File",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))

        aab_input_frame = ctk.CTkFrame(aab_frame, fg_color="transparent")
        aab_input_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.aab_entry = ctk.CTkEntry(
            aab_input_frame, textvariable=self.aab_path,
            placeholder_text="Select an .aab file...",
            height=38, font=ctk.CTkFont(size=13)
        )
        self.aab_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            aab_input_frame, text="Browse", width=90, height=38,
            command=self._browse_aab,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right")

        # ── Keystore Section ──
        ks_container = ctk.CTkFrame(self.main_frame, corner_radius=12)
        ks_container.pack(fill="x", pady=(0, 10))

        ks_header = ctk.CTkFrame(ks_container, fg_color="transparent")
        ks_header.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkLabel(
            ks_header, text="🔑 Keystore Signing (Optional)",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left")

        self.ks_switch = ctk.CTkSwitch(
            ks_header, text="", variable=self.use_keystore,
            command=self._toggle_keystore, width=48
        )
        self.ks_switch.pack(side="right")

        self.ks_fields_frame = ctk.CTkFrame(ks_container, fg_color="transparent")
        self.ks_fields_frame.pack(fill="x", padx=15, pady=(0, 12))

        # Keystore file
        ks_file_frame = ctk.CTkFrame(self.ks_fields_frame, fg_color="transparent")
        ks_file_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(ks_file_frame, text="Keystore file:", width=110, anchor="w",
                      font=ctk.CTkFont(size=12)).pack(side="left")
        self.ks_entry = ctk.CTkEntry(ks_file_frame, textvariable=self.keystore_path,
                                      placeholder_text=".jks / .keystore", height=34,
                                      font=ctk.CTkFont(size=12))
        self.ks_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ks_browse_btn = ctk.CTkButton(ks_file_frame, text="Browse", width=70, height=34,
                                            command=self._browse_keystore,
                                            font=ctk.CTkFont(size=12))
        self.ks_browse_btn.pack(side="right")

        # Keystore password
        ks_pass_frame = ctk.CTkFrame(self.ks_fields_frame, fg_color="transparent")
        ks_pass_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(ks_pass_frame, text="KS Password:", width=110, anchor="w",
                      font=ctk.CTkFont(size=12)).pack(side="left")
        self.ks_pass_entry = ctk.CTkEntry(ks_pass_frame, textvariable=self.ks_pass,
                                           show="•", placeholder_text="Keystore password",
                                           height=34, font=ctk.CTkFont(size=12))
        self.ks_pass_entry.pack(side="left", fill="x", expand=True)

        # Key alias
        alias_frame = ctk.CTkFrame(self.ks_fields_frame, fg_color="transparent")
        alias_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(alias_frame, text="Key Alias:", width=110, anchor="w",
                      font=ctk.CTkFont(size=12)).pack(side="left")
        self.alias_entry = ctk.CTkEntry(alias_frame, textvariable=self.key_alias,
                                         placeholder_text="Key alias name",
                                         height=34, font=ctk.CTkFont(size=12))
        self.alias_entry.pack(side="left", fill="x", expand=True)

        # Key password
        key_pass_frame = ctk.CTkFrame(self.ks_fields_frame, fg_color="transparent")
        key_pass_frame.pack(fill="x", pady=(0, 0))
        ctk.CTkLabel(key_pass_frame, text="Key Password:", width=110, anchor="w",
                      font=ctk.CTkFont(size=12)).pack(side="left")
        self.key_pass_entry = ctk.CTkEntry(key_pass_frame, textvariable=self.key_pass,
                                            show="•", placeholder_text="Key password",
                                            height=34, font=ctk.CTkFont(size=12))
        self.key_pass_entry.pack(side="left", fill="x", expand=True)

        # Initially hide keystore fields
        self.ks_fields_frame.pack_forget()

        # ── Convert Button ──
        self.convert_btn = ctk.CTkButton(
            self.main_frame, text="🚀  Convert to APK", height=48,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_convert,
            corner_radius=10
        )
        self.convert_btn.pack(fill="x", pady=(5, 10))

        # ── Progress Bar ──
        self.progress = ctk.CTkProgressBar(self.main_frame, height=6, corner_radius=3)
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)

        # ── Log Section ──
        log_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        log_frame.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkLabel(
            log_header, text="📋 Logs",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            log_header, text="Clear", width=60, height=28,
            command=self._clear_logs, fg_color="gray",
            font=ctk.CTkFont(size=11)
        ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            log_frame, font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8, height=200, wrap="word",
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Configure log colors
        self.log_box.tag_config("info", foreground="#60a5fa")
        self.log_box.tag_config("success", foreground="#4ade80")
        self.log_box.tag_config("error", foreground="#f87171")
        self.log_box.tag_config("warn", foreground="#fbbf24")
        self.log_box.tag_config("dim", foreground="#6b7280")

    def _check_dependencies(self):
        """Check Java and bundletool on startup."""
        self.log("Checking dependencies...", "info")

        # Check Java
        java_ok, java_ver = check_java()
        if java_ok:
            self.log(f"✅ Java found: {java_ver}", "success")
        else:
            self.log("❌ Java not found! Please install Java JRE/JDK.", "error")
            self.log("   Download: https://adoptium.net/", "dim")
            self.convert_btn.configure(state="disabled")
            return

        # Check bundletool
        bt_path = get_bundletool_path()
        if bt_path:
            self.log(f"✅ bundletool.jar found", "success")
            self.log(f"   Path: {bt_path}", "dim")
        else:
            self.log("❌ bundletool.jar not found!", "error")
            self.log("   Place bundletool.jar next to this application.", "dim")
            self.convert_btn.configure(state="disabled")
            return

        self.log("Ready to convert!", "success")
        self.log("─" * 50, "dim")

    def _toggle_keystore(self):
        """Show/hide keystore fields."""
        if self.use_keystore.get():
            self.ks_fields_frame.pack(fill="x", padx=15, pady=(0, 12))
        else:
            self.ks_fields_frame.pack_forget()

    def _browse_aab(self):
        path = filedialog.askopenfilename(
            title="Select AAB file",
            filetypes=[("Android App Bundle", "*.aab"), ("All files", "*.*")]
        )
        if path:
            self.aab_path.set(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.log(f"Selected: {os.path.basename(path)} ({size_mb:.1f} MB)", "info")

    def _browse_keystore(self):
        path = filedialog.askopenfilename(
            title="Select Keystore file",
            filetypes=[("Keystore", "*.jks *.keystore"), ("All files", "*.*")]
        )
        if path:
            self.keystore_path.set(path)
            self.log(f"Keystore: {os.path.basename(path)}", "info")

    def _clear_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def log(self, message, tag="info"):
        """Append message to log panel (thread-safe)."""
        def _append():
            self.log_box.configure(state="normal")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_box.insert("end", f"[{timestamp}] {message}\n", tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        # Schedule on main thread if called from another thread
        self.after(0, _append)

    def _start_convert(self):
        """Validate inputs and start conversion in background thread."""
        if self.converting:
            return

        aab = self.aab_path.get().strip()
        if not aab or not os.path.isfile(aab):
            messagebox.showwarning("Warning", "Please select a valid .aab file.")
            return

        if not aab.lower().endswith('.aab'):
            messagebox.showwarning("Warning", "File must have .aab extension.")
            return

        if self.use_keystore.get():
            ks = self.keystore_path.get().strip()
            if not ks or not os.path.isfile(ks):
                messagebox.showwarning("Warning", "Please select a valid keystore file.")
                return
            if not self.ks_pass.get().strip():
                messagebox.showwarning("Warning", "Please enter keystore password.")
                return
            if not self.key_alias.get().strip():
                messagebox.showwarning("Warning", "Please enter key alias.")
                return
            if not self.key_pass.get().strip():
                messagebox.showwarning("Warning", "Please enter key password.")
                return

        # Disable UI during conversion
        self.converting = True
        self.convert_btn.configure(state="disabled", text="⏳  Converting...")
        self.progress.set(0)

        thread = threading.Thread(target=self._do_convert, daemon=True)
        thread.start()

    def _do_convert(self):
        """Run the conversion in a background thread."""
        temp_dir = None
        try:
            aab_file = self.aab_path.get().strip()
            aab_dir = os.path.dirname(aab_file)
            aab_name = os.path.splitext(os.path.basename(aab_file))[0]
            output_apk = os.path.join(aab_dir, f"{aab_name}.apk")

            bundletool_jar = get_bundletool_path()
            if not bundletool_jar:
                self.log("❌ bundletool.jar not found!", "error")
                return

            # Create temp directory for intermediate files
            temp_dir = tempfile.mkdtemp(prefix="aab2apk_")
            apks_file = os.path.join(temp_dir, f"{aab_name}.apks")

            self.log("─" * 50, "dim")
            self.log(f"Input:  {aab_file}", "info")
            self.log(f"Output: {output_apk}", "info")
            self._update_progress(0.1)

            # Build command
            cmd = [
                'java', '-jar', bundletool_jar,
                'build-apks',
                f'--bundle={aab_file}',
                f'--output={apks_file}',
                '--mode=universal',
                '--overwrite'
            ]

            # Add keystore args if enabled
            if self.use_keystore.get():
                ks = self.keystore_path.get().strip()
                self.log(f"🔑 Signing with keystore: {os.path.basename(ks)}", "info")
                cmd.extend([
                    f'--ks={ks}',
                    f'--ks-pass=pass:{self.ks_pass.get().strip()}',
                    f'--ks-key-alias={self.key_alias.get().strip()}',
                    f'--key-pass=pass:{self.key_pass.get().strip()}'
                ])
            else:
                self.log("🔓 Signing with debug key (no custom keystore)", "warn")

            self._update_progress(0.2)

            # Run bundletool
            self.log("⚙️  Running bundletool build-apks...", "info")
            self.log(f"Command: java -jar bundletool.jar build-apks --mode=universal ...", "dim")

            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creation_flags
            )

            # Stream output to log
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    self.log(f"   {line}", "dim")

            process.wait()
            self._update_progress(0.6)

            if process.returncode != 0:
                self.log(f"❌ bundletool failed with exit code {process.returncode}", "error")
                return

            self.log("✅ build-apks completed", "success")

            # Check .apks file exists
            if not os.path.isfile(apks_file):
                self.log("❌ .apks file was not created.", "error")
                return

            self._update_progress(0.7)

            # Extract universal.apk from .apks (it's a ZIP file)
            self.log("📦 Extracting universal.apk from .apks bundle...", "info")

            try:
                with zipfile.ZipFile(apks_file, 'r') as zf:
                    # Find the universal APK inside
                    apk_entries = [n for n in zf.namelist() if n.endswith('.apk')]
                    if not apk_entries:
                        self.log("❌ No .apk found in .apks bundle!", "error")
                        return

                    self.log(f"   Found: {', '.join(apk_entries)}", "dim")

                    # Extract universal.apk (or the first apk)
                    target_entry = 'universal.apk' if 'universal.apk' in apk_entries else apk_entries[0]
                    extracted_path = os.path.join(temp_dir, target_entry)
                    zf.extract(target_entry, temp_dir)

                    self._update_progress(0.85)

                    # Move to output location
                    if os.path.exists(output_apk):
                        os.remove(output_apk)
                    shutil.move(extracted_path, output_apk)

            except zipfile.BadZipFile:
                self.log("❌ .apks file is corrupted (not a valid ZIP).", "error")
                return

            self._update_progress(1.0)

            # Final info
            apk_size_mb = os.path.getsize(output_apk) / (1024 * 1024)
            self.log("─" * 50, "dim")
            self.log(f"🎉 Conversion successful!", "success")
            self.log(f"   Output: {output_apk}", "success")
            self.log(f"   Size: {apk_size_mb:.2f} MB", "success")

            if self.use_keystore.get():
                self.log(f"   Signed with: {os.path.basename(self.keystore_path.get())}", "success")
            else:
                self.log(f"   Signed with: debug key", "warn")

        except Exception as e:
            self.log(f"❌ Unexpected error: {str(e)}", "error")
        finally:
            # Cleanup temp files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    self.log("🗑️  Cleaned up temporary files.", "dim")
                except Exception:
                    pass

            # Re-enable UI
            self.after(0, self._reset_ui)

    def _update_progress(self, value):
        """Update progress bar (thread-safe)."""
        self.after(0, lambda: self.progress.set(value))

    def _reset_ui(self):
        """Reset UI after conversion."""
        self.converting = False
        self.convert_btn.configure(state="normal", text="🚀  Convert to APK")


if __name__ == "__main__":
    app = AABConverterApp()
    app.mainloop()
