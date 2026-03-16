import ssl
import certifi

def check_netfree_ca():
    # בדיקת הנתיב שבו certifi משתמש
    cert_path = certifi.where()
    print(f"Checking certificates in: {cert_path}")
    
    # חיפוש המילה NetFree בתוך קובץ התעודות
    try:
        with open(cert_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "NetFree" in content:
                print("✅ תעודת נטפרי נמצאה בתוך מאגר certifi!")
            else:
                print("❌ תעודת נטפרי לא נמצאה במאגר certifi.")
    except Exception as e:
        print(f"Error reading cert file: {e}")

    # בדיקה אם ה-SSL Context מצליח לטעון אותה
    context = ssl.create_default_context()
    found_netfree = False
    for cert in context.get_ca_certs():
        # בדיקה בשדות ה-Subject של התעודה
        subject = str(cert.get('subject', ''))
        if 'NetFree' in subject:
            found_netfree = True
            print(f"✅ תעודה מאומתת נמצאה ב-Context: {subject}")
            break
    
    if not found_netfree:
        print("❌ ה-SSL Context של פייתון לא מזהה את נטפרי.")

if __name__ == "__main__":
    check_netfree_ca()