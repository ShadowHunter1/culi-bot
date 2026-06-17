# Playbook Metadata

ID: configmap-secret

Category: configuration

Priority: high

Keywords:
- configmap
- secret
- env
- envfrom
- projected
- volume
- subpath
- configuration

Related Alerts:
- CreateContainerConfigError
- SecretNotFound
- ConfigMapNotFound
- InvalidEnvironmentVariableNames

---
# ConfigMap / Secret / Projected Config

## 1. Nhóm lỗi chính
- missing config → object/key không tồn tại hoặc sai namespace
- wrong reference → sai name/key/path/env mapping
- env injection issue → envFrom/env/valueFrom sai hoặc bị override
- mount issue → volume/subPath/items sai hoặc permission lỗi
- config update misunderstanding → env không update / subPath không update / delay
- secret encoding/permission issue → base64 sai / mode sai

---

## 2. Symptom → hướng xử lý

- symptom: Pod không start / CreateContainerConfigError  
  - nghĩ ngay: missing config hoặc key sai  
  - check trước: `kubectl describe pod` → missing secret/config  
  - phân biệt với: app crash (container start rồi mới fail)

- symptom: thiếu env trong app  
  - nghĩ ngay: envFrom skip invalid key hoặc override  
  - check trước: events (`InvalidEnvironmentVariableNames`) + `printenv`  
  - phân biệt với: app parse sai env

- symptom: file config không tồn tại  
  - nghĩ ngay: items/path/subPath sai hoặc optional  
  - check trước: volume spec + mountPath  
  - phân biệt với: storage issue (PVC)

- symptom: key not found  
  - nghĩ ngay: key không tồn tại hoặc encode sai  
  - check trước: `kubectl get cm/secret -o yaml`  
  - phân biệt với: app parse config sai

- symptom: update config nhưng app không đổi  
  - nghĩ ngay: env không update hoặc subPath  
  - check trước: config inject kiểu gì (env vs volume)  
  - phân biệt với: app caching

- symptom: permission denied khi đọc file  
  - nghĩ ngay: defaultMode / fs permission  
  - check trước: `ls -l` trong container  
  - phân biệt với: app bug

- symptom: CrashLoopBackOff sau khi đổi config  
  - nghĩ ngay: config invalid / format sai  
  - check trước: logs + timeline change  
  - phân biệt với: deploy image mới

---

## 3. Playbook nhanh

- bước 1: xác định config injection  
  - env → env/envFrom/valueFrom  
  - file → volume / projected  

- bước 2: nếu pod không start  
  - `describe pod` → events (missing/mount/env)  

- bước 3: verify object & key  
  - configmap/secret tồn tại  
  - key đúng  
  - namespace đúng  

- bước 4: verify runtime  
  - env → `printenv`  
  - file → `ls/cat` mountPath  

---

## 4. Common mismatches

- name != object name  
- namespace mismatch  
- key != actual key  
- envFrom chứa key invalid → bị skip  
- env override nhau  
- subPath dùng với config → không update  
- optional=true → config rỗng nhưng không fail  
- secret base64 sai / có newline  
- defaultMode/mode sai → permission fail  
- kustomize secret hash → reference bị drift  

---

## 5. Mental shortcuts

- Pod không start → check describe pod trước  
- env thiếu → nghi envFrom skip hoặc override  
- mount rỗng → nghi optional hoặc items sai  
- update không effect → hỏi ngay: env hay volume?  
- volume update chậm → do kubelet delay  
- subPath → không bao giờ auto-update  
- permission denied → mode/securityContext  
- Crash sau config change → config invalid  

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

- `kubectl describe pod`  
- `kubectl get pod -o yaml`  
- `kubectl get configmap -o yaml`  
- `kubectl get secret -o yaml`  
- `kubectl logs --previous`  
- `kubectl exec -- printenv`  
- `kubectl exec -- ls -la <mountPath>`  

---

## 7. Nhầm lẫn phổ biến

- config issue vs app bug  
- env vs volume behavior (env không update)  
- subPath vẫn update (thực tế không)  
- secret tồn tại nhưng sai namespace  
- optional che giấu lỗi config  
- encoding base64 vs plaintext  
- config update nhưng pod không restart  
