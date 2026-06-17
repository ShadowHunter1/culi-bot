# Playbook Metadata

ID: storage-pv-pvc

Category: storage

Priority: high

Keywords:
- pvc
- pv
- storageclass
- csi
- volume
- mount
- attach
- provisioning
- volumeattachment

Related Alerts:
- PersistentVolumeClaimPending
- FailedMount
- FailedAttachVolume
- VolumeProvisioningFailed

---
# Storage (PV / PVC / Volume)

## 1. Nhóm lỗi chính
- PVC binding issue → không tìm được PV phù hợp
- dynamic provisioning issue → CSI/provisioner không hoạt động
- attach/detach issue → volume không attach được vào node
- mount issue → kubelet không mount được volume
- access mode / volumeMode mismatch → cấu hình không phù hợp workload
- permission / filesystem issue → app không đọc/ghi được
- topology / storage constraint issue → zone/node không match

---

## 2. Symptom → hướng xử lý

- symptom: PVC Pending  
  - nghĩ ngay: không có PV match hoặc provisioning fail  
  - check trước: `describe pvc` + storageClass + accessModes + volumeMode  
  - phân biệt với: WaitForFirstConsumer (có thể bình thường)

- symptom: Pod Pending + unbound PVC  
  - nghĩ ngay: PVC chưa bound (Immediate mode)  
  - check trước: PVC status + storageClass.volumeBindingMode  
  - phân biệt với: scheduling issue (CPU/taint)

- symptom: FailedMount / ContainerCreating lâu  
  - nghĩ ngay: mount fail (node/kubelet)  
  - check trước: pod events (kubelet)  
  - phân biệt với: attach fail (controller-level)

- symptom: FailedAttachVolume / Multi-Attach  
  - nghĩ ngay: volume attach fail / conflict giữa node  
  - check trước: VolumeAttachment + pod events  
  - phân biệt với: mount issue

- symptom: Pod Running nhưng app crash (storage-related)  
  - nghĩ ngay: permission / data / volumeMode mismatch  
  - check trước: logs + volumeMode (Filesystem vs Block)  
  - phân biệt với: mount failure

- symptom: Permission denied / Read-only filesystem  
  - nghĩ ngay: fsGroup / UID / ownership mismatch  
  - check trước: securityContext + volumeMount  
  - phân biệt với: accessMode hiểu sai

---

## 3. Playbook nhanh

- bước 1: xác định stage  
  - PVC Pending → binding/provisioning  
  - FailedAttach → attach  
  - FailedMount → mount  
  - Running nhưng lỗi → permission/app  

- bước 2: nếu PVC Pending  
  - kiểm tra PV match (size, accessModes, volumeMode)  
  - kiểm tra storageClass / provisioner  

- bước 3: nếu Pod Pending  
  - kiểm tra unbound PVC vs scheduling  

- bước 4: nếu Bound nhưng fail  
  - attach → VolumeAttachment  
  - mount → kubelet events  
  - permission → fsGroup / app logs  

---

## 4. Common mismatches

- PVC size > PV size → không bind  
- accessModes không match (RWO/RWX/ROX/RWOP)  
- volumeMode mismatch (Filesystem vs Block)  
- storageClassName sai → không provisioning  
- storageClassName="" → disable dynamic provisioning  
- provisioner không tồn tại / CSI chưa cài  
- topology mismatch (zone/node)  
- mountOptions không hợp lệ  
- app cần filesystem nhưng dùng block volume  

---

## 5. Mental shortcuts

- PVC Pending → check PV match trước  
- Pending + unbound PVC → không phải CPU/scheduling  
- FailedAttach → attach stage (controller)  
- FailedMount → mount stage (node)  
- Bound ≠ usable → vẫn có thể fail attach/mount  
- Running nhưng lỗi → permission/app, không phải storage system  
- Multi-Attach → volume chỉ attach được 1 node  
- WaitForFirstConsumer → Pending có thể bình thường  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe pvc`  
- `kubectl get pv` + `describe pv`  
- `kubectl get sc` + `describe sc`  
- `kubectl describe pod` (events)  
- `kubectl get events`  
- `kubectl get volumeattachment`  

---

## 7. Nhầm lẫn phổ biến

- PVC Pending vs lỗi thật (có thể do WaitForFirstConsumer)  
- Pod Pending do storage vs do scheduling  
- mount issue vs permission issue  
- PVC Bound nhưng volume chưa usable  
- accessModes = enforcement (thực tế không phải, trừ RWOP)  
- block vs filesystem bị dùng sai  
- dynamic provisioning bị disable mà không biết  
