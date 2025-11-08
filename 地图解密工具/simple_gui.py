import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import subprocess
import zipfile
import sys
import threading
import time
import json
import datetime

# Configuración del tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def load_config():
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r') as f:
                return json.load(f)
    except:
        pass
    return {"server_key": "", "last_used": "", "auto_load": True}

def save_config(config):
    try:
        config["last_used"] = datetime.datetime.now().isoformat()
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Could not save config: {e}")
 
class SimpleDecryptorGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌸 Fivem 地图解锁器 🌸")
        self.root.geometry("700x650")  # Taller window
        self.root.minsize(650, 600)    # Minimum size
        
        # Get script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.python_exe = sys.executable
        
        # Load saved configuration
        self.config = load_config()
        self.server_key = self.config.get("server_key", "")
        self.selected_items = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🌸 Fivem 地图解锁器 🌸",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Frame for server key
        key_frame = ctk.CTkFrame(main_frame)
        key_frame.pack(fill="x", padx=20, pady=10)
        
        key_label = ctk.CTkLabel(key_frame, text="🔑 服务器密钥 (必填):", font=ctk.CTkFont(size=14, weight="bold"))
        key_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        key_container = ctk.CTkFrame(key_frame, fg_color="transparent")
        key_container.pack(fill="x", padx=20, pady=(0, 10))
        
        self.key_entry = ctk.CTkEntry(
            key_container,
            placeholder_text="在此输入服务器密钥..." if not self.server_key else "密钥已保存 ✅",
            height=35
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # If we already have a saved key, show it partially
        if self.server_key:
            masked_key = f"{self.server_key[:8]}...{self.server_key[-4:]}"
            self.key_entry.insert(0, masked_key)
            self.key_entry.configure(state="disabled")
        
        load_key_btn = ctk.CTkButton(
            key_container,
            text="🔄 更换密钥" if self.server_key else "💫 加载密钥",
            command=self.load_key,
            width=120,
            height=35
        )
        load_key_btn.pack(side="right")
        
        # Frame for file selection
        files_frame = ctk.CTkFrame(main_frame)
        files_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        files_label = ctk.CTkLabel(
            files_frame,
            text="📁 选择文件:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        files_label.pack(anchor="w", padx=20, pady=(10, 10))
        
        # Selection buttons
        buttons_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=5)
        
        select_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="🗂️ 选择文件夹",
            command=self.select_folder,
            width=150,
            height=35
        )
        select_folder_btn.pack(side="left", padx=(0, 10))
        
        select_zip_btn = ctk.CTkButton(
            buttons_frame,
            text="📦 选择ZIP/RAR",
            command=self.select_archive,
            width=150,
            height=35
        )
        select_zip_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ 清空已选文件",
            command=self.clear_selection,
            width=100,
            height=35
        )
        clear_btn.pack(side="right")
        
        # File list
        self.files_text = ctk.CTkTextbox(
            files_frame,
            height=100,  # Reduced to give more space
            font=ctk.CTkFont(size=11)
        )
        self.files_text.pack(fill="x", padx=20, pady=(10, 15))
        self.update_files_display()
        
        # Bottom frame - Progress and main button
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", padx=20, pady=(5, 20))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(bottom_frame, height=20)
        self.progress.pack(fill="x", padx=20, pady=(15, 10))
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text="🌟 准备解锁! 选择文件并点击解锁按钮! 🌟",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=5)
        
        # MAIN DECRYPT BUTTON - MORE VISIBLE
        decrypt_btn = ctk.CTkButton(
            bottom_frame,
            text="🔮 点击开始解锁文件吧! 🔮",
            command=self.start_decryption,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=400,
            fg_color="#e94560",
            hover_color="#c73650",
            corner_radius=15
        )
        decrypt_btn.pack(pady=20)
        
        # Additional button to open results folder
        open_btn = ctk.CTkButton(
            bottom_frame,
            text="📂 打开破解后存放的文件夹",
            command=self.open_results,
            height=35,
            fg_color="#27ae60",
            hover_color="#229954"
        )
        open_btn.pack(pady=(0, 10))
        
    def load_key(self):
        # If we already have a saved key, allow changing it
        if self.server_key:
            response = messagebox.askyesno(
                "更换密钥", 
                "🔄 你已经有一个保存的服务器密钥.\n你是否想要更换为一个新的密钥?",
                icon="question"
            )
            if not response:
                return
            
            # Enable the field for editing
            self.key_entry.configure(state="normal")
            self.key_entry.delete(0, "end")
            
        key = self.key_entry.get().strip()
        
        # If the field is empty, ask them to enter one
        if not key:
            # If they had a saved key and deleted it, ask for a new one
            if self.server_key:
                self.key_entry.configure(placeholder_text="在此输入新的服务器密钥...")
            messagebox.showerror("Error", "🚫 请输入服务器密钥!")
            return
            
        self.server_key = key
        self.status_label.configure(text="🔄 正在验证和保存密钥...")
        
        def load_thread():
            try:
                # Test the key with escrow.py
                cmd = [self.python_exe, "escrow.py", "-k", self.server_key, "-s"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
                
                if result.returncode == 0:
                    # Save the configuration
                    self.config["server_key"] = self.server_key
                    save_config(self.config)
                    
                    # Update the UI
                    masked_key = f"{self.server_key[:8]}...{self.server_key[-4:]}"
                    self.key_entry.configure(state="normal")
                    self.key_entry.delete(0, "end")
                    self.key_entry.insert(0, masked_key)
                    self.key_entry.configure(state="disabled", placeholder_text="密钥已保存 ✅")
                    
                    self.status_label.configure(text="✅ 密钥验证保存成功! 你不需要再次输入! 🌟")
                else:
                    self.status_label.configure(text="❌ 无效的密钥. 请验证它是否正确.")
                    self.server_key = ""  # Reset if invalid
            except Exception as e:
                self.status_label.configure(text=f"❌ 验证密钥时出错: {str(e)}")
                self.server_key = ""  # Reset on error
                
        threading.Thread(target=load_thread, daemon=True).start()
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="选择要解锁的文件")
        if folder:
            self.selected_items.append(folder)
            self.update_files_display()
            
    def select_archive(self):
        files = filedialog.askopenfilenames(
            title="选择要解锁的压缩文件",
            filetypes=[
                ("所有压缩文件", "*.zip *.rar *.7z *.tar *.gz"),
                ("ZIP文件", "*.zip"),
                ("RAR文件", "*.rar"),
                ("7Z文件", "*.7z"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.selected_items.extend(files)
            self.update_files_display()
            
    def clear_selection(self):
        self.selected_items.clear()
        self.update_files_display()
        self.status_label.configure(text="🌸 已清空! 🌸")
        
    def update_files_display(self):
        self.files_text.delete("0.0", "end")
        if not self.selected_items:
            self.files_text.insert("0.0", "🌸 没有选择文件...\n\n请选择一些ZIP文件或文件夹进行解锁!")
        else:
            text = "📋 已选择文件:\n\n"
            for i, item in enumerate(self.selected_items, 1):
                name = os.path.basename(item)
                tipo = "📁 文件夹" if os.path.isdir(item) else "📦 压缩文件"
                text += f"{i}. {tipo}: {name}\n"
            text += f"\n🎌 总数: {len(self.selected_items)} 文件"
            self.files_text.insert("0.0", text)
    
    def extract_archive(self, archive_path, extract_to):
        """提取ZIP和其他格式文件"""
        try:
            file_ext = os.path.splitext(archive_path)[1].lower()
            print(f"正在提取 {archive_path} 到 {extract_to}")
            
            if file_ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                print(f"成功提取ZIP: {archive_path}")
                return True
            else:
                # Para RAR y otros, intentar con 7zip o WinRAR
                commands_to_try = [
                    ['7z', 'x', f'"{archive_path}"', f'-o"{extract_to}"', '-y'],
                    ['winrar', 'x', '-y', archive_path, f'{extract_to}\\'],
                    ['unrar', 'x', '-y', archive_path, extract_to]
                ]
                
                for cmd in commands_to_try:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"成功提取 with {cmd[0]}: {archive_path}")
                            return True
                    except FileNotFoundError:
                        continue
                
                print(f"提取 {archive_path} 失败 - 没有找到合适的提取器")
                return False
                
        except Exception as e:
            print(f"提取 {archive_path} 时出错: {e}")
            return False
    
    def start_decryption(self):
        if not self.selected_items:
            messagebox.showerror("Error", "🚫 请选择文件或文件夹进行解锁!")
            return
            
        if not self.server_key:
            messagebox.showerror("Error", "🚫 请先加载你的服务器密钥!")
            return
        
        def decrypt_thread():
            try:
                self.progress.set(0)
                total = len(self.selected_items)
                processed = 0
                successfully_processed = 0
                
                for item in self.selected_items:
                    name = os.path.basename(item)
                    self.status_label.configure(text=f"🔄 正在处理: {name}...")
                    
                    if os.path.isfile(item):  # It's a compressed file
                        file_ext = os.path.splitext(item)[1].lower()
                        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
                        
                        if file_ext in archive_extensions:
                            # Use the improved process_archive function via -z
                            print(f"正在处理压缩文件 with improved escrow.py: {item}")
                            cmd = [self.python_exe, "escrow.py", "-z", item]  # No need for -k, uses saved one
                            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir, timeout=300)
                            
                            print(f"压缩文件处理输出: {result.stdout}")
                            if result.stderr:
                                print(f"压缩文件处理错误: {result.stderr}")
                            
                            if result.returncode == 0:
                                successfully_processed += 1
                                print(f"成功处理压缩文件: {item}")
                            else:
                                print(f"处理压缩文件失败: {item}")
                                
                    elif os.path.isdir(item):  # It's a folder
                        # Process folder directly
                        print(f"正在处理文件夹: {item}")
                        cmd = [self.python_exe, "escrow.py", "-d", item]  # No need for -k, uses saved one
                        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir, timeout=300)
                        
                        if result.returncode == 0:
                            successfully_processed += 1
                            print(f"成功处理文件夹: {item}")
                        else:
                            print(f"处理文件夹失败: {item}")
                    
                    processed += 1
                    self.progress.set(processed / total)
                
                # Run watermark if files were processed
                if successfully_processed > 0:
                    self.status_label.configure(text="🌟 正在应用最终水印...")
                    watermark_cmd = [self.python_exe, "watermark.py", "-d", "./out"]
                    subprocess.run(watermark_cmd, cwd=self.script_dir, timeout=60)
                    
                    self.progress.set(1.0)
                    self.status_label.configure(text=f"✅ 完成! {successfully_processed} 文件处理成功! 🎌")
                    messagebox.showinfo("Success! 🌸", f"解锁完成!\n\n✅ {successfully_processed} 文件处理\n📁 查看 'out' 文件夹")
                else:
                    self.status_label.configure(text="❌ 无法处理选定的文件")
                    messagebox.showerror("Error 🚫", "无法处理选定的文件.\n\n请确保:\n• ZIP/RAR文件包含.fxap文件的文件夹\n• 服务器密钥有效\n• 文件未损坏")
                
            except subprocess.TimeoutExpired:
                self.status_label.configure(text="⏰ 处理超时")
                messagebox.showerror("Timeout", "处理时间过长已取消")
            except Exception as e:
                self.status_label.configure(text=f"❌ 处理时出错: {str(e)}")
                messagebox.showerror("Error", f"处理时出错:\n{str(e)}")
            
        threading.Thread(target=decrypt_thread, daemon=True).start()
    
    def open_results(self):
        """打开结果文件夹"""
        output_path = os.path.join(self.script_dir, "out")
        if os.path.exists(output_path):
            os.startfile(output_path)
        else:
            messagebox.showwarning("Notice", "🔍 文件夹不存在.\n请先运行解锁!")
    
    def run(self):
        self.root.mainloop()

def main():
    app = SimpleDecryptorGUI()
    app.run()

if __name__ == "__main__":
    main()
