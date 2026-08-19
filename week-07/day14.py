import base64
import json
import os
import secrets
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


TABLE_NAME = os.environ["TABLE_NAME"]
EXPECTED_TOKEN = os.environ.get("DEMO_TOKEN", "")
TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CloudAdhar Day 14 | DynamoDB Orders</title>
  <style>
    :root { --navy:#17233f; --blue:#2563eb; --sky:#eaf2ff; --green:#15803d;
      --amber:#b45309; --red:#b91c1c; --line:#dbe4f0; --muted:#64748b; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Arial,sans-serif; background:#f5f7fb; color:#172033; }
    header { background:linear-gradient(125deg,#111c35,#234aa5); color:white; padding:28px 5vw; }
    header h1 { margin:0 0 7px; font-size:clamp(25px,4vw,40px); }
    header p { margin:0; color:#dce8ff; }
    main { width:min(1180px,92vw); margin:24px auto 48px; }
    .toolbar,.card,.panel { background:white; border:1px solid var(--line); border-radius:16px;
      box-shadow:0 8px 24px rgba(23,35,63,.06); }
    .toolbar { padding:16px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
    input,select,button { font:inherit; border-radius:9px; padding:10px 12px; border:1px solid #bdc9d8; }
    input { flex:1; min-width:190px; }
    button { background:var(--blue); color:white; border-color:var(--blue); font-weight:700; cursor:pointer; }
    button.secondary { background:white; color:var(--navy); border-color:#9aabc0; }
    button:disabled { opacity:.55; cursor:not-allowed; }
    .grid { margin-top:18px; display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
    .card { padding:18px; }
    .label { font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); font-weight:800; }
    .value { font-size:24px; font-weight:850; margin-top:8px; }
    .panel { margin-top:18px; padding:20px; overflow:auto; }
    .panel h2 { margin:0 0 5px; }
    .panel .hint { color:var(--muted); margin:0 0 16px; font-size:14px; }
    table { width:100%; border-collapse:collapse; min-width:850px; }
    th,td { padding:12px 10px; text-align:left; border-bottom:1px solid #e8edf4; }
    th { color:#526174; font-size:12px; text-transform:uppercase; letter-spacing:.05em; }
    code { background:#eff4fa; padding:3px 6px; border-radius:6px; font-size:12px; }
    .badge { display:inline-block; padding:5px 9px; border-radius:999px; font-size:12px; font-weight:800; }
    .PAID,.COMPLETED,.DELIVERED { color:var(--green); background:#dcfce7; }
    .OPEN { color:var(--amber); background:#fef3c7; }
    .SHIPPED { color:#1d4ed8; background:#dbeafe; }
    .CANCELLED { color:var(--red); background:#fee2e2; }
    .result { margin-top:12px; padding:13px; border-radius:10px; background:var(--sky); display:none; }
    .error { background:#fee2e2; color:#8a1515; }
    .architecture { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; align-items:center; }
    .architecture div { padding:14px; text-align:center; background:#eff4fa; border-radius:10px; font-weight:750; }
    .architecture span { text-align:center; color:var(--blue); font-weight:900; }
    #login { position:fixed; inset:0; background:rgba(9,17,34,.76); display:flex; align-items:center;
      justify-content:center; z-index:20; padding:18px; }
    #loginBox { width:min(430px,100%); background:white; border-radius:18px; padding:25px; }
    #loginBox h2 { margin-top:0; }
    #loginBox input { width:100%; margin:8px 0 12px; }
    #loginError { color:var(--red); min-height:20px; }
    @media(max-width:850px) { .grid { grid-template-columns:repeat(2,1fr); }
      .architecture { grid-template-columns:1fr; } .architecture span { transform:rotate(90deg); } }
    @media(max-width:520px) { .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div id="login">
    <div id="loginBox">
      <h2>Day 14 Demo Access</h2>
      <p>Enter the private value stored in the Lambda <code>DEMO_TOKEN</code> environment variable.</p>
      <input id="tokenInput" type="password" placeholder="Demo token" autocomplete="off">
      <button onclick="login()">Open dashboard</button>
      <p id="loginError"></p>
    </div>
  </div>

  <header>
    <h1>CloudAdhar Order Dashboard</h1>
    <p>Day 14 · DynamoDB access patterns, indexes, TTL and Streams</p>
  </header>

  <main>
    <section class="toolbar">
      <input id="orderId" value="O9001" placeholder="Order ID, for example O9001">
      <button onclick="findOrder()">Find through GSI1</button>
      <button class="secondary" onclick="loadDashboard()">Refresh table query</button>
      <button class="secondary" onclick="logout()">Lock</button>
    </section>
    <div id="notice" class="result"></div>

    <section class="grid">
      <div class="card"><div class="label">Customer</div><div class="value" id="customer">—</div></div>
      <div class="card"><div class="label">Orders</div><div class="value" id="orderCount">—</div></div>
      <div class="card"><div class="label">Total value</div><div class="value" id="totalValue">—</div></div>
      <div class="card"><div class="label">TTL session</div><div class="value" id="ttl">—</div></div>
    </section>

    <section class="panel">
      <h2>Customer orders</h2>
      <p class="hint"><code>PK=CUSTOMER#C101</code> and <code>begins_with(SK, ORDER#)</code>, newest first.</p>
      <table>
        <thead><tr><th>Order</th><th>Product</th><th>Created</th><th>Total</th><th>Status</th><th>Change status</th></tr></thead>
        <tbody id="orders"><tr><td colspan="6">Loading…</td></tr></tbody>
      </table>
    </section>

    <section class="panel">
      <h2>GSI1 lookup result</h2>
      <p class="hint">Find an order without knowing the customer: <code>GSI1PK=ORDER#order-id</code>.</p>
      <div id="searchResult">Search for O9001.</div>
    </section>

    <section class="panel">
      <h2>What happens when status changes?</h2>
      <div class="architecture">
        <div>Browser UI</div><span>→</span><div>UI Lambda</div><span>→</span>
        <div>DynamoDB UpdateItem</div><span>→</span><div>Stream → Consumer Lambda → CloudWatch</div>
      </div>
    </section>
  </main>

  <script>
    const statuses = ['OPEN','PAID','SHIPPED','DELIVERED','COMPLETED','CANCELLED'];
    let token = sessionStorage.getItem('day14Token') || '';
    const money = n => new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n||0);
    const esc = value => String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

    async function api(path, options={}) {
      options.headers = {...(options.headers||{}), 'x-demo-token':token};
      const response = await fetch(path, options);
      const data = await response.json().catch(() => ({message:'Invalid server response'}));
      if (!response.ok) throw new Error(data.message || `Request failed: ${response.status}`);
      return data;
    }
    async function login() {
      const entered = document.getElementById('tokenInput').value.trim();
      if (entered) token = entered;
      if (!token) { document.getElementById('loginError').textContent='Enter the demo token.'; return; }
      sessionStorage.setItem('day14Token', token);
      try { await loadDashboard(); document.getElementById('login').style.display='none'; }
      catch (e) { sessionStorage.removeItem('day14Token'); document.getElementById('loginError').textContent=e.message; }
    }
    function logout() { sessionStorage.removeItem('day14Token'); token=''; document.getElementById('login').style.display='flex'; }
    function notify(message, bad=false) {
      const box=document.getElementById('notice'); box.textContent=message;
      box.className='result'+(bad?' error':''); box.style.display='block';
    }
    async function loadDashboard() {
      const data=await api('/api/dashboard');
      document.getElementById('customer').textContent=data.profile.Name || 'C101';
      document.getElementById('orderCount').textContent=data.orders.length;
      document.getElementById('totalValue').textContent=money(data.orders.reduce((s,o)=>s+Number(o.Total||0),0));
      const exp=Number(data.session.ExpiresAt||0);
      document.getElementById('ttl').textContent=exp ? new Date(exp*1000).toLocaleString('en-IN') : 'Not configured';
      document.getElementById('orders').innerHTML=data.orders.map(order => `
        <tr><td><strong>${esc(order.OrderId)}</strong><br><code>${esc(order.SK)}</code></td>
        <td>${esc(order.Product)}</td><td>${esc(order.CreatedAt)}</td><td>${money(order.Total)}</td>
        <td><span class="badge ${esc(order.Status)}">${esc(order.Status)}</span></td>
        <td><select id="s-${esc(order.OrderId)}">${statuses.map(s=>`<option ${s===order.Status?'selected':''}>${s}</option>`).join('')}</select>
        <button onclick='changeStatus(${JSON.stringify(order.PK)},${JSON.stringify(order.SK)},${JSON.stringify(order.CreatedAt)},${JSON.stringify(order.OrderId)})'>Update</button></td></tr>`).join('');
      return data;
    }
    async function findOrder() {
      try {
        const id=document.getElementById('orderId').value.trim().toUpperCase();
        const data=await api('/api/order?orderId='+encodeURIComponent(id));
        const o=data.order;
        document.getElementById('searchResult').innerHTML=o
          ? `<strong>${esc(o.OrderId)}</strong> belongs to <code>${esc(o.PK)}</code> · ${esc(o.Product)} · <span class="badge ${esc(o.Status)}">${esc(o.Status)}</span>`
          : 'No matching order.';
      } catch(e) { notify(e.message,true); }
    }
    async function changeStatus(pk,sk,createdAt,orderId) {
      try {
        const status=document.getElementById('s-'+orderId).value;
        await api('/api/status',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({pk,sk,createdAt,status})});
        notify(`${orderId} changed to ${status}. Now open the Stream consumer CloudWatch log.`);
        await loadDashboard();
      } catch(e) { notify(e.message,true); }
    }
    if (token) login();
  </script>
</body>
</html>"""


def plain(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, list):
        return [plain(v) for v in value]
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    return value


def response(status, body, content_type="application/json"):
    if content_type == "application/json" and not isinstance(body, str):
        body = json.dumps(plain(body))
    return {
        "statusCode": status,
        "headers": {
            "content-type": content_type,
            "cache-control": "no-store",
            "x-content-type-options": "nosniff",
        },
        "body": body,
    }


def authorized(event):
    headers = {str(k).lower(): str(v) for k, v in (event.get("headers") or {}).items()}
    supplied = headers.get("x-demo-token", "")
    return bool(EXPECTED_TOKEN) and secrets.compare_digest(supplied, EXPECTED_TOKEN)


def parse_body(event):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body)


def dashboard():
    profile = TABLE.get_item(Key={"PK": "CUSTOMER#C101", "SK": "PROFILE"}).get("Item", {})
    orders = TABLE.query(
        KeyConditionExpression=Key("PK").eq("CUSTOMER#C101") & Key("SK").begins_with("ORDER#"),
        ScanIndexForward=False,
    ).get("Items", [])
    session = TABLE.get_item(Key={"PK": "SESSION#S1001", "SK": "META"}).get("Item", {})
    return response(200, {"profile": profile, "orders": orders, "session": session})


def find_order(event):
    order_id = ((event.get("queryStringParameters") or {}).get("orderId") or "").strip().upper()
    if not order_id or len(order_id) > 30:
        return response(400, {"message": "Enter a valid order ID."})
    result = TABLE.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"ORDER#{order_id}"),
        Limit=1,
    )
    items = result.get("Items", [])
    return response(200, {"order": items[0] if items else None})


def update_status(event):
    data = parse_body(event)
    pk = str(data.get("pk", ""))
    sk = str(data.get("sk", ""))
    created_at = str(data.get("createdAt", ""))
    status = str(data.get("status", "")).upper()
    allowed = {"OPEN", "PAID", "SHIPPED", "DELIVERED", "COMPLETED", "CANCELLED"}
    if pk != "CUSTOMER#C101" or not sk.startswith("ORDER#") or status not in allowed or not created_at:
        return response(400, {"message": "Invalid order update."})
    result = TABLE.update_item(
        Key={"PK": pk, "SK": sk},
        UpdateExpression="SET #st = :st, LSI1SK = :lsi",
        ExpressionAttributeNames={"#st": "Status"},
        ExpressionAttributeValues={":st": status, ":lsi": f"STATUS#{status}#{created_at}"},
        ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
        ReturnValues="ALL_NEW",
    )
    return response(200, {"message": "Order updated", "order": result["Attributes"]})


def lambda_handler(event, context):
    method = ((event.get("requestContext") or {}).get("http") or {}).get("method", "GET")
    path = event.get("rawPath") or "/"

    if method == "GET" and path == "/":
        return response(200, HTML, "text/html; charset=utf-8")
    if not authorized(event):
        return response(401, {"message": "Incorrect demo token."})

    try:
        if method == "GET" and path == "/api/dashboard":
            return dashboard()
        if method == "GET" and path == "/api/order":
            return find_order(event)
        if method == "POST" and path == "/api/status":
            return update_status(event)
        return response(404, {"message": "Route not found."})
    except Exception as exc:
        print(json.dumps({"error": str(exc), "path": path}))
        return response(500, {"message": "Demo request failed. Check the Lambda logs and permissions."})
