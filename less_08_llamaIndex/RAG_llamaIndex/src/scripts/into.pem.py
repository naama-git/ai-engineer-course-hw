import certifi

# הנתיב המדויק מהסביבה הווירטואלית שלך
target_pem = certifi.where()
# נתיב התעודה של נטפרי
netfree_crt = r'C:\Users\User\Documents\netfree-ca.crt'

try:
    with open(netfree_crt, 'r') as f:
        cert_data = f.read()
    
    with open(target_pem, 'a') as f:
        f.write("\n# NetFree CA\n")
        f.write(cert_data)
        
    print(f"✅ התעודה הוזרקה בהצלחה לקובץ: {target_pem}")
except Exception as e:
    print(f"❌ שגיאה: {e}")