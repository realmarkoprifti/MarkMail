from MarkMail.settings import RECAPTCHA_SECRET
import requests

def check_captcha(captcha_value):
    recaptcha_request = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        'secret': RECAPTCHA_SECRET,
        'response': captcha_value
    })
    
    return recaptcha_request.json()["success"]