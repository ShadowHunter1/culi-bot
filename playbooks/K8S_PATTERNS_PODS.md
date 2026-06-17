
# Playbook Metadata

ID: pods

Category: workload

Priority: high

Keywords:
- pod
- pending
- containercreating
- crashloopbackoff
- imagepullbackoff
- errimagepull
- oomkilled
- probe
- restart

Related Alerts:
- PodPending
- CrashLoopBackOff
- ImagePullBackOff
- ErrImagePull
- OOMKilled
- FailedMount
- FailedCreatePodSandBox

---

# Pods

## 1. Nhóm lỗi chính
- scheduling / placement → pod không được assign node
- image / registry → pull image fail
- container runtime / CNI → không tạo được sandbox/network
- volume / config injection → mount hoặc inject fail
- application lifecycle → app crash / exit / restart loop
- probes (readiness / liveness / startup) → fail health check
- resource pressure / OOM / eviction → bị kill do resource

---

## 2. Symptom → hướng xử lý

- symptom: Pod Pending  
  - nghĩ ngay: chưa chắc là scheduling  
  - check trước: PodScheduled + events  
  - phân biệt với: PodScheduled=True → không phải scheduling

- symptom: ContainerCreating lâu  
  - nghĩ ngay: đang kẹt setup (CNI / volume / image)  
  - check trước: events (FailedMount / FailedCreatePodSandBox / pull error)  
  - phân biệt với: init container chưa xong (Init:*)

- symptom: ImagePullBackOff / ErrImagePull  
  - nghĩ ngay: image name / registry / auth  
  - check trước: events + imagePullSecret  
  - phân biệt với: network issue node → registry

- symptom: CrashLoopBackOff  
  - nghĩ ngay: app crash / config lỗi / probe / OOM  
  - check trước: `logs -p` + exitCode  
  - phân biệt với: pod bị recreate bởi controller

- symptom: Error / Failed  
  - nghĩ ngay: container exit non-zero hoặc config lỗi  
  - check trước: state.waiting / state.terminated  
  - phân biệt với: CrashLoopBackOff (restart loop)

- symptom: OOMKilled  
  - nghĩ ngay: vượt memory limit  
  - check trước: limits vs usage  
  - phân biệt với: eviction do node pressure

- symptom: Completed (Succeeded)  
  - nghĩ ngay: app đã exit 0  
  - check trước: logs + command  
  - phân biệt với: job pod vs long-running service

- symptom: probe failed  
  - nghĩ ngay: readiness/liveness/startup config sai  
  - check trước: endpoint + timing  
  - phân biệt với: app crash thật

- symptom: restart liên tục  
  - nghĩ ngay: app exit / probe / OOM / eviction  
  - check trước: restartCount + lastState  
  - phân biệt với: pod recreate (UID đổi)

---

## 3. Playbook nhanh

- bước 1: xác định layer  
  → PodScheduled + container state + events source

- bước 2: đọc events  
  → biết đang kẹt ở scheduling / image / CNI / volume / probe

- bước 3: lấy evidence  
  → logs (-p) + lastState (exitCode/reason)

- bước 4: debug sâu nếu cần  
  → kubectl debug / exec / inspect runtime

---

## 4. Common mismatches

- requests quá lớn → không schedule được  
- node labels / affinity / taints không match  
- image sai / thiếu registry credentials  
- configmap/secret key không tồn tại  
- securityContext không phù hợp (permission fail)  
- probe config không đúng timing/endpoint  
- memory limit quá thấp → OOMKilled  
- hostPort làm giảm số node hợp lệ  

---

## 5. Mental shortcuts

- Pending + PodScheduled=False → scheduling  
- ContainerCreating → CNI / volume / image  
- ImagePullBackOff → image / registry  
- CrashLoopBackOff → logs -p trước  
- OOMKilled → check memory limit trước  
- readiness fail → traffic issue, không phải restart  
- restart liên tục → phân biệt restart vs recreate  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe pod` → events (quan trọng nhất)  
- `kubectl get pod -o wide` → node / restart / age  
- `kubectl get pod -o yaml` → state + conditions  
- `kubectl logs` + `kubectl logs -p`  
- `kubectl debug` (khi cần shell/tool)  

---

## 7. Nhầm lẫn phổ biến

- Pending ≠ luôn là scheduling  
- STATUS của kubectl ≠ phase thực  
- CrashLoopBackOff ≠ pod bị recreate  
- readiness fail ≠ container restart  
- OOMKilled ≠ eviction  
- ContainerCreating ≠ app bug  
- Completed ≠ system đang chạy bình thường  
