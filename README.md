# 🔄 AAB to APK Converter

Ứng dụng Windows desktop chuyển đổi file **Android App Bundle (.aab)** sang **APK** với giao diện đồ họa. Hỗ trợ ký APK bằng keystore gốc.

## 📋 Yêu cầu

Chỉ cần **1 thứ duy nhất**:

- ✅ **Java JRE/JDK 11+** — [Tải tại đây (Adoptium)](https://adoptium.net/)

> Python, bundletool, và các thư viện khác đã được đóng gói sẵn trong file `.exe`, **không cần cài thêm**.

## 🚀 Sử dụng file AAB2APK.exe

### Bước 1: Tải về
- Tải file `AAB2APK.exe` từ [Releases](https://github.com/nghiact97/aab_to_apk_converter/releases)

### Bước 2: Kiểm tra Java
- Mở Command Prompt, chạy `java -version`
- Nếu chưa có, tải Java tại [adoptium.net](https://adoptium.net/)

### Bước 3: Chạy ứng dụng
1. Double-click `AAB2APK.exe` để mở
2. Nhấn **Browse** để chọn file `.aab` cần convert
3. *(Tuỳ chọn)* Bật **Sign with custom keystore** nếu muốn ký bằng keystore gốc:
   - Chọn file keystore (`.jks` / `.keystore`)
   - Nhập **Keystore Password**
   - Nhập **Key Alias**
   - Nhập **Key Password**
4. Nhấn **🚀 Convert to APK**
5. File APK sẽ được lưu **cùng thư mục** với file AAB gốc
6. Theo dõi quá trình convert trong panel **Logs** phía dưới

## 🔑 Về Keystore Signing

| Chế độ | Mô tả | Khi nào dùng |
|--------|--------|-------------|
| **Không dùng keystore** | APK ký bằng debug key | Test, cài trực tiếp |
| **Dùng keystore gốc** | APK ký bằng chữ ký của bạn | Phân phối, cập nhật app |

> ⚠️ Nếu muốn APK có cùng chữ ký với bản trên Google Play, bạn **phải** dùng đúng keystore đã ký AAB.

## 🔧 Build từ source (dành cho developer)

```bash
# Cài thư viện
py -3 -m pip install customtkinter pyinstaller

# Chạy trực tiếp
py -3 aab_converter.py

# Build .exe
build.bat
# Output: dist/AAB2APK.exe (~59 MB, bao gồm bundletool)
```

## 📁 Cấu trúc project

```
├── aab_converter.py   # Source code ứng dụng
├── build.bat          # Script build .exe
├── bundletool.jar     # Google Bundletool 1.18.3
├── README.md
└── dist/
    └── AAB2APK.exe    # Ứng dụng đã build
```

## 📋 Logs

Ứng dụng hiển thị real-time logs:
- 🔵 **Info** — Thông tin quá trình
- 🟢 **Success** — Thành công
- 🟡 **Warning** — Cảnh báo (VD: dùng debug key)
- 🔴 **Error** — Lỗi kèm chi tiết

## ❓ Xử lý lỗi thường gặp

| Lỗi | Giải pháp |
|-----|-----------|
| `Java not found` | Cài Java JRE/JDK và thêm vào PATH |
| `bundletool.jar not found` | Build lại `.exe` bằng `build.bat` |
| `unknown type 'macro'` | Bundletool quá cũ, cần version ≥ 1.15 |
| `Keystore was tampered with` | Sai password keystore |
