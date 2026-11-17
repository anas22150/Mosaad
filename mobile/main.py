import flet as ft
import httpx

DEFAULT_SERVER_URL = "https://YOUR-SERVER-DOMAIN"

def main(page: ft.Page):
    page.title = "خبير AI"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F3F6FC"
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    api_url = ft.TextField(label="رابط الخادم المنشور", value=DEFAULT_SERVER_URL,
                           border_radius=12)
    ask_box = ft.TextField(label="اكتب سؤالك", multiline=True, min_lines=3, max_lines=6,
                           border_radius=12)
    lesson_box = ft.TextField(label="الصق نص الدرس هنا", multiline=True, min_lines=5,
                              max_lines=12, border_radius=12)
    number = ft.Dropdown(label="عدد الأسئلة", value="10",
                         options=[ft.dropdown.Option(str(x)) for x in (5, 10, 15, 20, 25)])
    kind = ft.Dropdown(label="نوع الأسئلة", value="متنوع",
                       options=[ft.dropdown.Option(x) for x in
                                ("متنوع", "اختيار من متعدد", "صح أو خطأ", "أكمل", "مقالي")])
    output = ft.Text("ستظهر الإجابة هنا.", selectable=True, color="#1E293B")
    status = ft.Text("", color="#64748B")

    def notify(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    async def request(path, payload):
        base = (api_url.value or "").strip().rstrip("/")
        if not base or "YOUR-SERVER-DOMAIN" in base:
            notify("اكتب رابط الخادم بعد نشره أولًا.")
            return None
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(base + path, json=payload)
                r.raise_for_status()
                return r.json()
        except Exception as ex:
            notify("تعذر الاتصال بالخادم: " + str(ex))
            return None

    async def ask_click(e):
        if not (ask_box.value or "").strip():
            notify("اكتب سؤالك أولًا.")
            return
        status.value, output.value = "جاري تجهيز الإجابة...", ""
        page.update()
        data = await request("/ask", {"question": ask_box.value.strip()})
        if data:
            output.value = data.get("answer", str(data))
        status.value = ""
        page.update()

    async def exam_click(e):
        if not (lesson_box.value or "").strip():
            notify("أضف نص الدرس أولًا.")
            return
        status.value, output.value = "جاري إنشاء الامتحان...", ""
        page.update()
        data = await request("/generate-exam", {
            "lesson": lesson_box.value.strip(),
            "count": int(number.value or "10"),
            "kind": kind.value or "متنوع"
        })
        if data:
            output.value = data.get("exam", str(data))
        status.value = ""
        page.update()
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("خبير AI", size=28, weight=ft.FontWeight.BOLD, color="#172554"),
                ft.Text("مساعدك الذكي للفهم والمذاكرة", color="#64748B")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            bgcolor="white", padding=18, border_radius=20
        ),
        ft.Container(content=ft.Column([
            ft.Text("إعداد الاتصال", size=18, weight=ft.FontWeight.BOLD),
            api_url,
            ft.Text("لا تضع مفتاح API داخل التطبيق. المفتاح يُحفظ في إعدادات الخادم فقط.",
                    size=12, color="#64748B")
        ], spacing=10), bgcolor="white", padding=16, border_radius=18),
        ft.Container(content=ft.Column([
            ft.Text("اسأل خبير AI", size=19, weight=ft.FontWeight.BOLD, color="#1D4ED8"),
            ask_box,
            ft.Button("إرسال السؤال", icon=ft.Icons.AUTO_AWESOME,
                           on_click=ask_click,
                           style=ft.ButtonStyle(bgcolor="#2563EB", color="white"))
        ], spacing=12), bgcolor="white", padding=16, border_radius=18),
        ft.Container(content=ft.Column([
            ft.Text("إنشاء امتحان من الدرس", size=19, weight=ft.FontWeight.BOLD,
                    color="#6D28D9"),
            lesson_box, number, kind,
            ft.Button("إنشاء الامتحان", icon=ft.Icons.QUIZ,
                           on_click=exam_click,
                           style=ft.ButtonStyle(bgcolor="#6D28D9", color="white"))
        ], spacing=12), bgcolor="white", padding=16, border_radius=18),
        ft.Container(content=ft.Column([
            ft.Text("النتيجة", size=18, weight=ft.FontWeight.BOLD),
            status, output
        ], spacing=10), bgcolor="white", padding=16, border_radius=18),
        ft.Text("نسخة أولية: ميزات النص تعمل بعد نشر الخادم وإعداده.",
                size=11, color="#94A3B8", text_align=ft.TextAlign.CENTER)
    )

ft.run(main)
