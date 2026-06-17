# Playbook Metadata

ID: autoscaling

Category: workload

Priority: high

Keywords:
- hpa
- vpa
- cluster-autoscaler
- scaling
- metrics
- replicas
- utilization
- autoscaling

Related Alerts:
- HPAScalingFailed
- ScalingLimited
- MetricsUnavailable
- NotTriggerScaleUp
- VPARecommendationMissing

---

# Autoscaling

## 1. Nhóm lỗi chính
- HPA không scale → metrics không có / requests sai / HPA inactive
- HPA scale sai → metric không phản ánh bottleneck / config sai
- VPA không apply → updateMode / metrics / policy
- Cluster Autoscaler không scale node → pod không “fit” node mới
- scaling lag / delay → control loop + stabilization
- bounds/policy issue → bị cap bởi min/max hoặc policy

---

## 2. Symptom → hướng xử lý

- symptom: load tăng nhưng replicas không tăng  
  - nghĩ ngay: HPA không có metrics hoặc request sai  
  - check trước: `describe hpa` + Metrics API (`kubectl top`)  
  - phân biệt với: app bottleneck không nằm ở CPU/memory  

- symptom: HPA TARGET = `<unknown>`  
  - nghĩ ngay: metrics pipeline lỗi  
  - check trước: `metrics.k8s.io` + apiservices  
  - phân biệt với: selector HPA sai  

- symptom: scale lên rồi xuống liên tục (flapping)  
  - nghĩ ngay: thiếu stabilization / apply manifest override  
  - check trước: HPA behavior + có set `spec.replicas` không  
  - phân biệt với: rollout thay đổi pod  

- symptom: pod Pending nhưng cluster không scale node  
  - nghĩ ngay: CA không thể làm pod schedulable  
  - check trước: `describe pod` → `NotTriggerScaleUp`  
  - phân biệt với: Pending do image / PVC / init  

- symptom: VPA không thay đổi resources  
  - nghĩ ngay: updateMode không phải Recreate/InPlace  
  - check trước: `.status.recommendation` + updateMode  
  - phân biệt với: metrics không có  

- symptom: autoscaling gây churn  
  - nghĩ ngay: HPA flapping / VPA evict / CA scale up/down  
  - check trước: events HPA + mode VPA  
  - phân biệt với: deploy pipeline apply liên tục  

---

## 3. Playbook nhanh

- bước 1: xác định layer  
  - HPA → replicas  
  - VPA → requests/limits  
  - CA → node  

- bước 2: verify metrics pipeline  
  - `kubectl top`  
  - `metrics.k8s.io`  

- bước 3: check requests & bounds  
  - requests có set không  
  - HPA min/max  
  - VPA policy  
  - CA node group limits  

- bước 4: nếu có Pending pod  
  - check Unschedulable vs constraint  
  - đọc event CA  

---

## 4. Common mismatches

- metrics target != metrics available  
- requests sai → utilization sai → HPA sai  
- thiếu requests → HPA không hoạt động  
- min/max replicas cap HPA  
- CA không scale vì pod không fit node  
- VPA mode không đúng (Off/Initial)  
- VPA recommend > capacity cluster  
- HPA + manifest replicas override  
- HPA + VPA cùng CPU/memory gây conflict  

---

## 5. Mental shortcuts

- TARGET `<unknown>` → metrics pipeline  
- ScalingLimited → bị cap min/max  
- Pending + NotTriggerScaleUp → CA không giúp được  
- Pending + Insufficient → thiếu resource  
- VPA có recommendation nhưng không apply → updateMode  
- scale chậm → do control loop + stabilization  
- load tăng nhưng CPU không tăng → metric sai  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe hpa`  
- `kubectl get hpa -A`  
- `kubectl top pods / nodes`  
- `kubectl get --raw "/apis/metrics.k8s.io/v1beta1/pods"`  
- `kubectl get apiservices | grep metrics`  
- `kubectl describe pod` (FailedScheduling / CA events)  
- `kubectl logs cluster-autoscaler`  
- `kubectl get verticalpodautoscaler -A`  

---

## 7. Nhầm lẫn phổ biến

- autoscaling issue vs app bottleneck  
- HPA issue vs metrics pipeline issue  
- Pending do constraint vs thiếu node  
- HPA “chậm” vs behavior bình thường  
- VPA không apply vs updateMode Off  
- HPA + deploy pipeline conflict  
