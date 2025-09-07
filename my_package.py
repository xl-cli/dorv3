from api_request import get_package, send_api_request
from ui import clear_screen, pause, show_package_details
from auth_helper import AuthInstance

# Fetch my packages
def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None
    
    id_token = tokens.get("id_token")
    
    path = "api/v8/packages/quota-details"
    
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }
    
    print("Fetching my packages...")
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        print("Failed to fetch packages")
        print("Response:", res)
        pause()
        return None
    
    quotas = res["data"]["quotas"]
    
    clear_screen()
    print("===============================")
    print("My Packages")
    print("===============================")
    my_packages =[]
    num = 1
    for quota in quotas:
        quota_code = quota["quota_code"] # Can be used as option_code
        group_code = quota["group_code"]
        name = quota["name"]
        family_code = "N/A"
        
        print(f"fetching package no. {num} details...")
        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]
        
        print("===============================")
        print(f"Package {num}")
        print(f"Name: {name}")
        print(f"Quota Code: {quota_code}")
        print(f"Family Code: {family_code}")
        print(f"Group Code: {group_code}")
        print("===============================")
        
        my_packages.append({
            "number": num,
            "quota_code": quota_code,
        })
        
        print("Rebuy package? Input package number to rebuy, or '00' to back.")
        choice = input("Choice: ")
        if choice == "00":
            return None
        selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
        
        if not selected_pkg:
            print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
            continue
        
        is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"])
        if is_done:
            return None
        
        num += 1
        
    pause()
        