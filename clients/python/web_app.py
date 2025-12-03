"""
Web-Interface für SENVEND Kartenleser Tests
Flask-basierte Weboberfläche zum Durchführen von Zahlungstests
"""

from flask import Flask, render_template, request, jsonify, Response
import asyncio
import json
from datetime import datetime
import threading
import queue

import grpc
from gen.local.v1 import local_pb2_grpc
from gen.api.v1 import pay_pb2

app = Flask(__name__)

# Globale Konfiguration
config = {
    'terminal_ip': '127.0.0.1',
    'terminal_port': 11111
}

# Queue für Live-Updates
update_queues = []


def broadcast_update(data):
    """Sendet Updates an alle verbundenen Clients"""
    for q in update_queues[:]:
        try:
            q.put_nowait(data)
        except queue.Full:
            update_queues.remove(q)


async def perform_payment(amount_cents: int, min_age: int = None):
    """
    Führt eine Zahlung durch und sendet Live-Updates
    """
    url = f"{config['terminal_ip']}:{config['terminal_port']}"
    
    broadcast_update({
        'type': 'info',
        'message': f"Verbinde mit Terminal: {url}",
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        async with grpc.aio.insecure_channel(url) as channel:
            stub = local_pb2_grpc.PayServiceStub(channel)
            request_queue = asyncio.Queue()
            
            async def request_generator():
                pay_start = pay_pb2.PayStart(amount=amount_cents)
                if min_age:
                    pay_start.age_verification.CopyFrom(
                        pay_pb2.AgeStartRequest(min_age=min_age)
                    )
                
                broadcast_update({
                    'type': 'info',
                    'message': f'➡️ Sende PayStart: {amount_cents/100:.2f} EUR' + (f' (Alter ≥{min_age})' if min_age else ''),
                    'timestamp': datetime.now().isoformat()
                })
                yield pay_pb2.PayRequest(start=pay_start)
                
                while True:
                    req = await request_queue.get()
                    if req is None:
                        break
                    yield req
            
            broadcast_update({
                'type': 'success',
                'message': 'Verbindung hergestellt',
                'timestamp': datetime.now().isoformat()
            })
            
            response_stream = stub.Pay(request_generator())
            payment_approved = False
            
            async for response in response_stream:
                result_type = response.WhichOneof('result')
                
                if result_type == 'age_api_success':
                    reason = response.age_api_success.reason
                    if reason == pay_pb2.AGE_API_SUCCESS_REASON_VERIFICATION_STARTED:
                        broadcast_update({
                            'type': 'info',
                            'message': 'Altersverifikation gestartet',
                            'timestamp': datetime.now().isoformat()
                        })
                
                elif result_type == 'age_success':
                    broadcast_update({
                        'type': 'success',
                        'message': 'Altersverifikation erfolgreich',
                        'timestamp': datetime.now().isoformat()
                    })
                
                elif result_type == 'age_failure':
                    broadcast_update({
                        'type': 'error',
                        'message': 'Altersverifikation fehlgeschlagen',
                        'timestamp': datetime.now().isoformat()
                    })
                    await request_queue.put(None)
                    return False
                
                elif result_type == 'age_api_failure':
                    reason = response.age_api_failure.reason
                    reason_name = pay_pb2.AgeApiFailureReason.Name(reason)
                    broadcast_update({
                        'type': 'error',
                        'message': f'Altersverifikation API Fehler: {reason_name}',
                        'timestamp': datetime.now().isoformat()
                    })
                    await request_queue.put(None)
                    return False
                
                elif result_type == 'api_success':
                    reason = response.api_success.reason
                    if reason == pay_pb2.PAY_API_SUCCESS_REASON_PAYMENT_STARTED:
                        broadcast_update({
                            'type': 'success',
                            'message': f'Zahlung gestartet: {amount_cents/100:.2f} EUR',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif reason == pay_pb2.PAY_API_SUCCESS_REASON_GOODS_ISSUED_ACCEPTED:
                        broadcast_update({
                            'type': 'success',
                            'message': 'Warenausgabe bestätigt',
                            'timestamp': datetime.now().isoformat()
                        })
                
                elif result_type == 'approved':
                    broadcast_update({
                        'type': 'success',
                        'message': '✅ Zahlung genehmigt! Karte hat genug Guthaben.',
                        'timestamp': datetime.now().isoformat()
                    })
                    payment_approved = True
                    
                    broadcast_update({
                        'type': 'info',
                        'message': '➡️ Sende PayGoodsIssued (Waren ausgegeben)',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    goods_issued = pay_pb2.PayRequest(
                        goods_issued=pay_pb2.PayGoodsIssued(partial_amount=0)
                    )
                    await request_queue.put(goods_issued)
                
                elif result_type == 'success':
                    broadcast_update({
                        'type': 'success',
                        'message': '✓✓✓ Zahlung erfolgreich abgeschlossen! ✓✓✓',
                        'timestamp': datetime.now().isoformat()
                    })
                    await request_queue.put(None)
                    return True
                
                elif result_type == 'failure':
                    reason_field = response.failure.WhichOneof('reason')
                    reason_value = getattr(response.failure, reason_field, 'UNBEKANNT')
                    if isinstance(reason_value, int):
                        reason_name = pay_pb2.PayFailureReason.Name(reason_value)
                    else:
                        reason_name = str(reason_value)
                    
                    broadcast_update({
                        'type': 'error',
                        'message': f'Zahlung fehlgeschlagen: {reason_name}',
                        'timestamp': datetime.now().isoformat()
                    })
                    await request_queue.put(None)
                    return False
                
                elif result_type == 'api_failure':
                    reason = response.api_failure.reason
                    reason_name = pay_pb2.PayApiFailureReason.Name(reason)
                    broadcast_update({
                        'type': 'error',
                        'message': f'API Fehler: {reason_name}',
                        'timestamp': datetime.now().isoformat()
                    })
                    await request_queue.put(None)
                    return False
            
            if not payment_approved:
                broadcast_update({
                    'type': 'error',
                    'message': 'Zahlung wurde nicht genehmigt',
                    'timestamp': datetime.now().isoformat()
                })
                return False
            
    except grpc.aio.AioRpcError as e:
        broadcast_update({
            'type': 'error',
            'message': f'gRPC Fehler: {e.code()} - {e.details()}',
            'timestamp': datetime.now().isoformat()
        })
        return False
    except asyncio.CancelledError:
        broadcast_update({
            'type': 'error',
            'message': 'Verbindung abgebrochen',
            'timestamp': datetime.now().isoformat()
        })
        return False
    except Exception as e:
        broadcast_update({
            'type': 'error',
            'message': f'Fehler: {type(e).__name__}: {e}',
            'timestamp': datetime.now().isoformat()
        })
        return False


def run_payment_async(amount_cents, min_age=None):
    """Führt Zahlung in neuem Event Loop aus (für Thread-Kompatibilität)"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(perform_payment(amount_cents, min_age))
        return result
    finally:
        loop.close()


@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Terminal-Konfiguration abrufen oder setzen"""
    if request.method == 'POST':
        data = request.json
        config['terminal_ip'] = data.get('terminal_ip', config['terminal_ip'])
        config['terminal_port'] = int(data.get('terminal_port', config['terminal_port']))
        return jsonify({'status': 'success', 'config': config})
    else:
        return jsonify(config)


@app.route('/api/test', methods=['POST'])
def api_test():
    """Startet einen Zahlungstest"""
    data = request.json
    amount_cents = int(data.get('amount', 100))
    min_age = data.get('min_age', None)
    if min_age:
        min_age = int(min_age)
    
    # Starte Zahlung in separatem Thread
    def run_test():
        run_payment_async(amount_cents, min_age)
    
    thread = threading.Thread(target=run_test)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/api/stream')
def stream():
    """Server-Sent Events Stream für Live-Updates"""
    def event_stream():
        q = queue.Queue(maxsize=10)
        update_queues.append(q)
        
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            update_queues.remove(q)
    
    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("=" * 60)
    print("  SENVEND Kartenleser Web-Interface")
    print("=" * 60)
    print()
    print("  Öffnen Sie: http://localhost:5000")
    print()
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
