# Playbook Metadata

ID: workload-management

Category: workload

Priority: high

Keywords:
- deployment
- replicaset
- statefulset
- daemonset
- job
- cronjob
- rollout
- reconcile
- controller

Related Alerts:
- ProgressDeadlineExceeded
- RolloutStuck
- FailedCreate
- StatefulSetStuck
- JobFailed
- CronJobMissed

---

# Workload Management

## 1. Nhóm lỗi chính
- rollout/update → rollout không progress hoặc stuck
- desired != actual replicas → controller không đạt số replica mong muốn
- controller không tạo pod → bị chặn bởi quota / RBAC / admission
- pod bị recreate ngoài mong đợi → controller reconciliation
- job/cronjob không chạy đúng → policy/time semantics
- stateful workload issue → ordering / storage / update strategy
- daemonset placement issue → node không eligible

---

## 2. Symptom → hướng xử lý

- symptom: rollout stuck  
  - nghĩ ngay: pod mới không Ready  
  - check trước: rollout status + pod events  
  - phân biệt với: scheduling issue (Pending)

- symptom: ProgressDeadlineExceeded  
  - nghĩ ngay: rollout không progress kịp thời  
  - check trước: deployment conditions + pod status  
  - phân biệt với: đây không phải root cause

- symptom: replicas không lên  
  - nghĩ ngay: controller bị chặn hoặc pod không chạy  
  - check trước: FailedCreate vs pod Pending  
  - phân biệt với: scheduling vs controller issue

- symptom: pod bị recreate  
  - nghĩ ngay: controller đang reconcile  
  - check trước: ownerReferences  
  - phân biệt với: restart trong cùng pod

- symptom: StatefulSet stuck  
  - nghĩ ngay: ordering / storage / update strategy  
  - check trước: ordinal pod + PVC + readiness  
  - phân biệt với: pod/app issue

- symptom: Job failed / retry  
  - nghĩ ngay: backoffLimit / activeDeadlineSeconds  
  - check trước: job conditions + pod logs  
  - phân biệt với: app exit expected

- symptom: CronJob không trigger  
  - nghĩ ngay: suspend / concurrency / deadline / timezone  
  - check trước: cronjob spec + events  
  - phân biệt với: job runtime issue

- symptom: DaemonSet thiếu pod trên node  
  - nghĩ ngay: nodeSelector / taints / affinity  
  - check trước: node labels + tolerations  
  - phân biệt với: pod crash trên node

---

## 3. Playbook nhanh

- bước 1: controller đã reconcile chưa  
  → generation vs observedGeneration

- bước 2: phân loại lỗi  
  - không tạo pod → controller-level  
  - có pod → pod-level

- bước 3: xác định workload type  
  - Deployment → ReplicaSet  
  - StatefulSet → ordinal  
  - DaemonSet → node placement  
  - Job/CronJob → retry / schedule

- bước 4: fix theo nguyên nhân chính  
  - controller issue → quota/RBAC  
  - pod issue → debug pod  
  - rollout issue → rollback/fix template  

---

## 4. Common mismatches

- selector != labels → pod không match hoặc bị reject  
- selector overlap → pod bị “adopt” ngoài ý muốn  
- strategy != expectation  
  - paused deployment → không rollout  
  - OnDelete (StatefulSet/DaemonSet) → không auto update  
- template change != rollout  
  - chỉ thay spec.template mới tạo revision  
- Job config mismatch  
  - parallelism=0 → job không chạy  
  - restartPolicy ảnh hưởng retry  
- CronJob config mismatch  
  - concurrencyPolicy=Forbid → skip run  
  - startingDeadlineSeconds quá thấp  
- StatefulSet prerequisites thiếu  
  - headless service / PVC / storage  

---

## 5. Mental shortcuts

- ProgressDeadlineExceeded → pod không Ready  
- FailedCreate → controller bị chặn  
- rollout không xảy ra → check paused / template change  
- StatefulSet stuck → check ordering + storage  
- Job retry loop → backoffLimit  
- CronJob không chạy → suspend / concurrency / deadline  
- pod tự recreate → controller reconcile  
- DaemonSet thiếu pod → node eligibility  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe <workload>` → conditions + events  
- `kubectl rollout status <type>/<name>`  
- `kubectl get rs` (Deployment)  
- `kubectl get pods -o wide`  
- `kubectl describe pod`  
- `kubectl events --for <resource>`  
- `kubectl logs --previous` (job/pod crash)  

---

## 7. Nhầm lẫn phổ biến

- rollout issue vs pod issue  
- controller issue vs scheduling issue  
- pod recreate vs container restart  
- CronJob issue vs Job issue  
- StatefulSet stuck vs app lỗi  
- paused deployment nhưng tưởng rollout fail  
- sửa CronJob nhưng Job cũ vẫn chạy  
