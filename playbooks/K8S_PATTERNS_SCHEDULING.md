# Playbook Metadata

ID: scheduling-placement

Category: scheduling

Priority: high

Keywords:

* scheduling
* placement
* affinity
* anti-affinity
* taint
* toleration
* topology spread
* preemption
* node selector

Related Alerts:

* FailedScheduling
* PodPending
* Unschedulable

---

# Scheduling / Placement

## 1. Nhóm lỗi chính

### selector / affinity mismatch

Không có node nào match.

### taint / toleration mismatch

Node từ chối pod.

### pod affinity / anti-affinity conflict

Không còn node hợp lệ.

### topology spread constraint fail

Phân bố không thỏa điều kiện.

### resource requests không fit

Scheduler reject dù node trông còn trống.

### priority / preemption không hiệu quả

Không giải quyết được constraint cứng.

### scheduling bị block

* schedulingGates
* custom scheduler

---

## 2. Symptom → hướng xử lý

### Pod Pending lâu

#### Nghĩ ngay

Chưa chắc là scheduling.

Có thể là:

* image
* volume
* runtime

#### Check trước

`kubectl describe pod`

→ PodScheduled + events

#### Phân biệt với

Nếu:

`PodScheduled=True`

→ không phải scheduling.

---

### 0/N nodes are available / FailedScheduling

#### Nghĩ ngay

Không có node feasible.

#### Check trước

Message cụ thể trong event:

* affinity
* taint
* resource
* spread

#### Phân biệt với

* node NotReady
* node cordoned

---

### node affinity / selector mismatch

#### Nghĩ ngay

Label node không match constraint.

#### Check trước

* node labels
* pod spec

#### Phân biệt với

preferred affinity (soft) vẫn schedule được.

---

### untolerated taint

#### Nghĩ ngay

Node có taint.

Pod thiếu toleration.

#### Check trước

* `kubectl describe node`
* tolerations

#### Phân biệt với

`.spec.nodeName` bypass scheduler.

---

### pod vào sai node

#### Nghĩ ngay

* constraint là soft (preferred)
* có constraint khác loại node đó

#### Check trước

* required vs preferred
* labels
* taints
* resource

#### Phân biệt với

Node bị thay đổi sau khi schedule.

Pod không reschedule.

---

### pod anti-affinity conflict

#### Nghĩ ngay

* topologyKey
* label không consistent

#### Check trước

* existing pods
* topology labels

#### Phân biệt với

resource issue song song.

---

### topology spread fail

#### Nghĩ ngay

* DoNotSchedule
* skew
* minDomains

không thỏa điều kiện.

#### Check trước

* topologyKey
* eligible nodes
* domains

#### Phân biệt với

nodeSelector làm giảm domain.

---

### Insufficient cpu/memory nhưng node còn trống

#### Nghĩ ngay

Request quá cao.

Scheduler dùng request, không dùng usage.

#### Check trước

* requests
* node allocatable

#### Phân biệt với

resource pressure runtime.

---

### preemption không giúp

#### Nghĩ ngay

Constraint mismatch.

Không phải thiếu resource.

#### Check trước

* preemptionPolicy
* constraint feasibility

#### Phân biệt với

resource shortage thật.

---

### Pending + SchedulingGated

#### Nghĩ ngay

Bị block bởi scheduling gate.

#### Check trước

`.spec.schedulingGates`

#### Phân biệt với

FailedScheduling thông thường.

---

## 3. Playbook nhanh

### Bước 1

Xác định có phải scheduling không

→ PodScheduled=False + FailedScheduling

---

### Bước 2

Đọc message scheduler

Map vào nhóm:

* affinity
* taint
* spread
* resource
* preemption

---

### Bước 3

Verify cluster state nhanh

* node Ready
* labels
* taints
* resource fit (requests)

---

### Bước 4

Fix theo hướng ít rủi ro

* giảm constraint (required → preferred nếu hợp lý)
* fix label
* fix toleration
* giảm request
* tăng capacity

---

## 4. Common mismatches

* node labels != selector / affinity
* nodeSelector + nodeAffinity cùng tồn tại nhưng không match
* taint != toleration (effect/operator sai)
* topologyKey không tồn tại trên node
* minDomains / maxSkew không phù hợp cluster
* requests quá cao so với capacity
* preemption kỳ vọng giải quyết constraint mismatch
* storage topology làm pod không schedulable

---

## 5. Mental shortcuts

* 0/N nodes available → check scheduler message ngay
* didn't match node affinity → label mismatch
* untolerated taint → thiếu toleration
* didn't satisfy topology spread → spread constraint quá chặt
* Insufficient cpu/memory → request không fit
* No preemption victims → không phải resource issue
* Pending nhưng PodScheduled=True → không phải scheduling

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

* `kubectl describe pod <pod>` → events (quan trọng nhất)
* `kubectl get pod -o wide` → đã có node chưa
* `kubectl get nodes` → trạng thái node
* `kubectl describe node` → taints + allocatable
* `kubectl get nodes --show-labels` → label mismatch
* `kubectl get events --sort-by=.lastTimestamp`

---

## 7. Nhầm lẫn phổ biến

* Pending do scheduling vs do image/volume
* resource usage thấp nhưng vẫn không schedule (do request)
* anti-affinity vs insufficient resources
* preemption không giải quyết constraint mismatch
* update label nhưng pod không di chuyển
* storage issue bị nhầm thành scheduling issue
