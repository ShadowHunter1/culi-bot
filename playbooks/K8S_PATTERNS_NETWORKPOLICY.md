# Playbook Metadata

ID: networkpolicy

Category: networking

Priority: high

Keywords:
- networkpolicy
- ingress
- egress
- podselector
- namespaceselector
- dns
- connectivity
- isolation

Related Alerts:
- NetworkPolicyDenied
- ConnectionTimeout
- DNSResolutionFailed

---

# NetworkPolicy

## 1. Nhóm lỗi chính
- ingress blocked → pod đích bị isolate, không nhận traffic
- egress blocked → pod nguồn bị isolate, không ra được
- selector mismatch → podSelector / namespaceSelector không match
- namespace scope mismatch → hiểu sai scope namespaced
- port / protocol mismatch → sai port hoặc TCP/UDP
- default deny side effects → chặn DNS / chặn nhầm ingress

---

## 2. Symptom → hướng xử lý

- symptom: connection timeout  
  - nghĩ ngay: bị block bởi NetworkPolicy  
  - check trước: cả egress (source) và ingress (dest) có allow không  
  - phân biệt với: connection refused (thường là app/port)

- symptom: chỉ một số pod connect được  
  - nghĩ ngay: selector mismatch (labels không giống nhau)  
  - check trước: labels pod OK vs pod fail  
  - phân biệt với: service selector mismatch

- symptom: cross-namespace fail  
  - nghĩ ngay: namespaceSelector không match  
  - check trước: namespace labels + selector  
  - phân biệt với: DNS query sai namespace

- symptom: DNS resolve fail  
  - nghĩ ngay: egress policy chặn DNS (UDP/TCP 53)  
  - check trước: có default deny egress không  
  - phân biệt với: CoreDNS/service DNS lỗi

- symptom: trước chạy được, apply policy xong fail  
  - nghĩ ngay: pod bị isolate bởi policy mới  
  - check trước: policyTypes + podSelector  
  - phân biệt với: rollout app/service change

- symptom: resolve OK nhưng connect fail  
  - nghĩ ngay: NetworkPolicy hoặc port mismatch  
  - check trước: endpoints + port + policy  
  - phân biệt với: service không có endpoint

---

## 3. Playbook nhanh

- bước 1: phân loại DNS vs connectivity  
  - DNS fail → DNS/policy  
  - DNS OK → connectivity/policy  

- bước 2: xác định source và destination  
  - pod nào gọi → pod nào  
  - port / protocol  

- bước 3: kiểm tra isolation  
  - source có egress policy không  
  - dest có ingress policy không  

- bước 4: verify rule  
  - selector match chưa  
  - namespace match chưa  
  - port/protocol đúng chưa  

---

## 4. Common mismatches

- podSelector != pod labels  
- namespaceSelector != namespace labels  
- quên namespaceSelector → chỉ match cùng namespace  
- selector nhiều điều kiện nhưng hiểu nhầm OR (thực tế là AND)  
- protocol mặc định TCP nhưng traffic là UDP  
- service port ≠ targetPort  
- default deny egress chặn DNS  
- quên policyTypes → block nhầm ingress  
- named port không match container port  

---

## 5. Mental shortcuts

- timeout → nghĩ ngay NetworkPolicy  
- refused → nghĩ app/port  
- DNS fail → check egress DNS trước  
- cross-namespace fail → check namespaceSelector  
- pod A OK, pod B fail → label mismatch  
- resolve OK + timeout → policy  
- resolve OK + refused → app  
- apply policy xong fail → isolate issue  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl get netpol -A`  
- `kubectl describe netpol`  
- `kubectl get pod --show-labels`  
- `kubectl get ns --show-labels`  
- `kubectl get svc` + `kubectl get endpointslice`  
- `nslookup <svc>.<ns>` từ pod  
- `kubectl get pods -n kube-system -l k8s-app=kube-dns`  

---

## 7. Nhầm lẫn phổ biến

- NetworkPolicy vs Service issue  
- NetworkPolicy vs app không listen  
- timeout do policy vs do network bên ngoài  
- DNS issue vs policy block DNS  
- selector không match vs service selector mismatch  
- nghĩ NetworkPolicy có “deny rule” (thực tế chỉ allow)  
- nghĩ policy target theo service (thực tế theo pod)  
