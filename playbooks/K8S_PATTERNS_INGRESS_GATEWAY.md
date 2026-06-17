# Playbook Metadata

ID: ingress-gateway

Category: ingress

Priority: high

Keywords:
- ingress
- gateway
- httproute
- tls
- host
- path
- ingressclass
- loadbalancer

Related Alerts:
- IngressUnavailable
- TLSHandshakeFailed
- BackendUnavailable
- HTTP404
- HTTP503

---

# Ingress / Gateway

## 1. Nhóm lỗi chính
- host / path routing mismatch → request không match rule
- ingress class / controller mismatch → controller không xử lý ingress
- backend service mapping issue → service không có endpoint hoặc sai port
- TLS termination / cert issue → handshake fail / cert sai
- default backend / fallback routing → rơi vào default route (404)
- exposure chain issue → LB / DNS / external path bị lỗi trước ingress

---

## 2. Symptom → hướng xử lý

- symptom: 404 từ ingress  
  - nghĩ ngay: host/path không match rule  
  - check trước: ingress rules + host header + pathType  
  - phân biệt với: backend trả 404 (service vẫn OK)

- symptom: 503 từ ingress  
  - nghĩ ngay: service không có endpoint hoặc sai port  
  - check trước: endpointslice + service port/targetPort  
  - phân biệt với: ingress mismatch (thường 404)

- symptom: TLS handshake fail  
  - nghĩ ngay: secret sai / host mismatch / SNI issue  
  - check trước: tls.secret + tls.hosts vs rules.host  
  - phân biệt với: app backend TLS mismatch

- symptom: host không match  
  - nghĩ ngay: sai Host header / wildcard không match  
  - check trước: rules.host + DNS trỏ đúng chưa  
  - phân biệt với: service/DNS nội bộ

- symptom: path route sai backend  
  - nghĩ ngay: precedence/pathType mismatch  
  - check trước: longest path + Exact vs Prefix  
  - phân biệt với: app routing

- symptom: truy cập ngoài không vào được  
  - nghĩ ngay: LB / DNS / ingress address chưa ready  
  - check trước: ingress ADDRESS + service LB  
  - phân biệt với: routing issue (thường vẫn có HTTP response)

- symptom: HTTP OK nhưng HTTPS fail  
  - nghĩ ngay: TLS config sai  
  - check trước: secret + host match  
  - phân biệt với: backend expect HTTPS

---

## 3. Playbook nhanh

- bước 1: kiểm tra external endpoint  
  - ingress ADDRESS có chưa  
  - DNS trỏ đúng chưa  

- bước 2: verify routing rule  
  - host  
  - path + pathType  

- bước 3: verify controller ownership  
  - ingressClassName đúng controller  

- bước 4: verify backend service  
  - service port/targetPort  
  - endpoints ready  

---

## 4. Common mismatches

- host != request host  
- wildcard host hiểu sai  
- path != request path  
- Prefix vs Exact sai expectation  
- ingressClass != controller  
- backend service port != config  
- service selector → không có endpoint  
- TLS secret != host  
- TLS secret thiếu key  
- LB address thay đổi nhưng DNS chưa update  

---

## 5. Mental shortcuts

- 404 → routing mismatch  
- 503 → backend/service issue  
- TLS fail → secret/host mismatch  
- timeout → LB / network / exposure chain  
- ADDRESS pending → chưa có external endpoint  
- internal OK + external fail → ingress/LB  
- ingress match OK + upstream fail → service  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl get ingress -A -o wide`  
- `kubectl describe ingress`  
- `kubectl get ingressclass`  
- `kubectl get svc -o yaml`  
- `kubectl get endpointslice`  
- `kubectl get secret <tls>`  
- `kubectl describe gateway / httproute` (nếu dùng Gateway API)  

---

## 7. Nhầm lẫn phổ biến

- ingress issue vs service issue  
- TLS issue vs backend app issue  
- external LB issue vs ingress config  
- host mismatch vs DNS nội bộ  
- path mismatch vs app routing  
- HTTP success nhưng HTTPS fail (termination misunderstanding)  
