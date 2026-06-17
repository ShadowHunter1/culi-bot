# Playbook Metadata

ID: services-dns

Category: networking

Priority: high

Keywords:

* service
* endpoint
* endpointslice
* dns
* clusterip
* targetport
* selector
* kube-proxy

Related Alerts:

* ServiceUnavailable
* EndpointMissing
* DNSResolutionFailed
* ConnectionRefused
* ConnectionTimeout

---

# Services / Endpoints / DNS

## 1. Nhóm lỗi chính

### service selector mismatch

Không chọn được pod backend.

### endpoint empty / not ready

Không có backend usable.

### port / targetPort mismatch

Connect sai port.

### DNS resolution issue

Resolve sai hoặc không resolve được.

### service type / access path mismatch

Dùng sai cách truy cập:

* ClusterIP
* NodePort
* ExternalName

### app không listen đúng port

Backend không phục vụ request.

---

## 2. Symptom → hướng xử lý

### no endpoints available

#### Nghĩ ngay

* selector mismatch
* pod chưa Ready

#### Check trước

* EndpointSlice
* Pod labels

#### Phân biệt với

* DNS issue (không resolve)

---

### connection refused

#### Nghĩ ngay

* sai port
* sai targetPort
* app không listen

#### Check trước

* Service port mapping
* test PodIP:port

#### Phân biệt với

* NetworkPolicy (thường timeout)

---

### connection timed out

#### Nghĩ ngay

* NetworkPolicy
* CNI
* Routing

#### Check trước

* endpoint tồn tại không
* network policy

#### Phân biệt với

* selector mismatch (endpoint = none)

---

### không resolve được service

#### Nghĩ ngay

* sai namespace
* DNS lỗi

#### Check trước

* nslookup
* resolv.conf
* CoreDNS

#### Phân biệt với

* endpoint issue (resolve OK nhưng connect fail)

---

### resolve OK nhưng connect fail

#### Nghĩ ngay

* endpoint issue
* port mismatch
* app issue

#### Check trước

* EndpointSlice
* PodIP:targetPort

#### Phân biệt với

* DNS issue

---

### traffic vào sai backend

#### Nghĩ ngay

* selector sai
* match nhầm pod

#### Check trước

* selector
* pod labels

#### Phân biệt với

* DNS gọi nhầm namespace

---

### intermittent connectivity

#### Nghĩ ngay

* pod restart
* endpoint churn
* unhealthy backend

#### Check trước

* restart count
* test từng endpoint

#### Phân biệt với

* NetworkPolicy (thường fail ổn định)

---

## 3. Playbook nhanh

### Bước 1: kiểm tra DNS

* nslookup service
* test kubernetes.default

### Bước 2: kiểm tra Service spec

* selector
* port
* targetPort

### Bước 3: kiểm tra EndpointSlice

* có endpoint không
* ready hay không

### Bước 4: test theo chain

Name → ClusterIP → PodIP

* PodIP fail → app issue
* ClusterIP fail → service proxy
* Name fail → DNS

---

## 4. Common mismatches

* selector != pod labels → endpoint rỗng
* port != targetPort → connect fail
* targetPort (string) ≠ numeric → mapping sai
* named port ≠ container port
* protocol mismatch (TCP/UDP)
* DNS namespace mismatch
* headless vs ClusterIP expectation
* ExternalName nhưng expect có endpoint

---

## 5. Mental shortcuts

* endpoints = none → selector sai
* resolve OK + connect fail → không phải DNS
* refused → port/app issue
* timeout → network policy / drop
* PodIP OK + ClusterIP fail → kube-proxy issue
* internal OK + external fail → ingress/LB
* intermittent → pod churn / unhealthy

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

* `kubectl get svc -o yaml`
* `kubectl describe svc`
* `kubectl get endpointslice`
* `kubectl get pods -l <selector>`
* `kubectl describe pod`
* `nslookup`
* `kubectl logs -n kube-system -l k8s-app=kube-dns`

---

## 7. Nhầm lẫn phổ biến

* service issue vs ingress issue
* service issue vs network policy issue
* DNS issue vs endpoint issue
* app không listen vs service config sai
* resolve sai namespace vs selector sai
* headless service vs ClusterIP behavior
