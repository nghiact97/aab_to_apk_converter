# 🔄 AAB to APK Converter

Ứng dụng Windows desktop chuyển đổi file **Android App Bundle (.aab)** sang **APK** với giao diện đồ họa. Hỗ trợ ký APK bằng keystore gốc.

## 📋 Yêu cầu

- **Windows** 10/11
- **Java JRE/JDK** 11+ — [Tải tại đây](https://adoptium.net/)

## 🚀 Sử dụng

### Cách 1: Chạy file .exe (khuyến nghị)

1. Mở file `dist/AAB2APK.exe`
2. Chọn file `.aab` cần convert bằng nút **Browse**
3. *(Tuỳ chọn)* Bật **Sign with custom keystore** nếu muốn ký bằng keystore gốc:
   - Chọn file keystore (`.jks` / `.keystore`)
   - Nhập **Keystore Password**
   - Nhập **Key Alias**
   - Nhập **Key Password**
4. Nhấn **🚀 Convert to APK**
5. File APK sẽ được lưu **cùng thư mục** với file AAB

### Cách 2: Chạy từ source

```bash
# Cài thư viện
py -3 -m pip install customtkinter

# Chạy
py -3 aab_converter.py
```

## 🔑 Về Keystore Signing

| Chế độ | Mô tả |
|--------|--------|
| **Không dùng keystore** | APK được ký bằng debug key — dùng để test |
| **Dùng keystore gốc** | APK được ký bằng chữ ký của bạn — dùng để phân phối |

> ⚠️ **Lưu ý:** Nếu muốn APK có cùng chữ ký với bản trên Google Play, bạn **phải** dùng đúng keystore đã ký AAB.

## 🔧 Build .exe từ source

```bash
# Chạy script build (tự cài dependencies)
build.bat

# Output: dist/AAB2APK.exe (~59 MB, đã bao gồm bundletool)
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

Ứng dụng hiển thị real-time logs trong panel phía dưới:
- 🔵 **Info** — Thông tin quá trình chạy
- 🟢 **Success** — Thành công
- 🟡 **Warning** — Cảnh báo (VD: dùng debug key)
- 🔴 **Error** — Lỗi (kèm chi tiết để debug)

## ❓ Xử lý lỗi thường gặp

| Lỗi | Giải pháp |
|-----|-----------|
| `Java not found` | Cài Java JRE/JDK và thêm vào PATH |
| `bundletool.jar not found` | Đặt `bundletool.jar` cùng thư mục với `.exe` hoặc build lại |
| `unknown type 'macro'` | Bundletool quá cũ, cần version ≥ 1.15 |
| `Keystore was tampered with` | Sai password keystore |
