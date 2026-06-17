# Playbook Metadata

ID: nodes-resources

Category: node

Priority: high

Keywords:
- node
- resource
- oomkilled
- eviction
- memorypressure
- diskpressure
- pidpressure
- allocatable
- requests
- limits

Related Alerts:
- OOMKilled
- Evicted
- NodeNotReady
- MemoryPressure
- DiskPressure
- PIDPressure
- FailedScheduling

---

# Nodes / Resources

## 1. Nhóm lỗi chính
- insufficient resources (scheduling) → không fit requests
- OOMKilled → vượt memory limit / node OOM
- eviction → kubelet kill pod để bảo vệ node
- node pressure → MemoryPressure / DiskPressure / PIDPressure
- node NotReady / unreachable → mất heartbeat / kubelet issue
- requests / limits / allocatable mismatch → config sai dẫn tới lỗi cả scheduling và runtime

---

## 2. Symptom → hướng xử lý

- symptom: Pod Pending + FailedScheduling  
  - nghĩ ngay: requests > allocatable  
  - check trước: scheduler message + node allocatable  
  - phân biệt với: affinity / taints / constraints

- symptom: OOMKilled (exit 137)  
  - nghĩ ngay: vượt memory limit hoặc node OOM  
  - check trước: memory limits + node pressure  
  - phân biệt với: app crash bình thường

- symptom: Pod Evicted  
  - nghĩ ngay: node pressure hoặc vượt ephemeral-storage  
  - check trước: node conditions + eviction reason  
  - phân biệt với: manual delete / rollout

- symptom: DiskPressure / MemoryPressure / PIDPressure  
  - nghĩ ngay: node thiếu resource tương ứng  
  - check trước: node conditions + filesystem usage  
  - phân biệt với: pod-level resource issue

- symptom: Node NotReady / unreachable  
  - nghĩ ngay: kubelet chết / network / node issue  
  - check trước: node conditions + taints  
  - phân biệt với: workload issue

- symptom: restart nhiều / latency cao  
  - nghĩ ngay: resource pressure (OOM / eviction / throttling)  
  - check trước: restart reason + node condition  
  - phân biệt với: app bug / probe fail

- symptom: app chậm nhưng không lỗi  
  - nghĩ ngay: CPU throttling  
  - check trước: CPU limits  
  - phân biệt với: insufficient CPU scheduling

---

## 3. Playbook nhanh

- bước 1: phân loại layer  
  - Pending → scheduling  
  - OOMKilled → container  
  - Evicted → node  
  - NotReady → node health  

- bước 2: nếu scheduling  
  - đọc `FailedScheduling`  
  - so requests vs allocatable  

- bước 3: nếu runtime  
  - OOM → check limits  
  - Evicted → check node pressure  

- bước 4: nếu node issue  
  - check node conditions + taints  
  - xem kubelet / node logs  

---

## 4. Common mismatches

- requests quá thấp → node bị pressure / eviction  
- limits quá thấp → OOMKilled  
- requests quá cao → Pending  
- capacity ≠ allocatable → hiểu sai khả năng node  
- ephemeral-storage không set → eviction bất ngờ  
- autoscaling kỳ vọng ≠ resource thực tế  
- CPU limits gây throttling  

---

## 5. Mental shortcuts

- FailedScheduling + Insufficient → requests không fit  
- OOMKilled → check memory limit trước  
- Evicted → node đang “tự cứu mình”  
- DiskPressure → disk node đầy (nodefs/imagefs)  
- MemoryPressure → node thiếu RAM  
- Node NotReady → node/kubelet issue  
- “free resource nhưng vẫn Pending” → do requests, không phải usage  
- app chậm + có CPU limit → nghĩ throttling  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe pod` → events + reason  
- `kubectl get events -A`  
- `kubectl get nodes`  
- `kubectl describe node` → conditions + allocatable  
- `kubectl get node -o yaml`  
- `kubectl top node / pod` (nếu có metrics)  
- node logs (kubelet / journalctl)  

---

## 7. Nhầm lẫn phổ biến

- OOMKilled vs app crash  
- Evicted vs manual delete  
- Pending do resource vs do constraint khác  
- node issue vs workload issue  
- “còn resource nhưng không schedule được” (do requests)  
- disk usage thật vs kubelet accounting  
- CPU throttling vs thiếu CPU  
