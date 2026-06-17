# Playbook Metadata

ID: auth-rbac-serviceaccount

Category: security

Priority: high

Keywords:

* rbac
* role
* rolebinding
* clusterrole
* clusterrolebinding
* serviceaccount
* authentication
* authorization
* token
* impersonation

Related Alerts:

* Forbidden
* Unauthorized
* RBACDenied
* ServiceAccountPermissionDenied

---

# Authentication / Authorization / RBAC / ServiceAccount

## 1. Nhóm lỗi chính

### RBAC deny

Không có rule allow phù hợp.

### sai service account

Pod dùng ServiceAccount không như mong đợi.

Ví dụ:

* default ServiceAccount

### binding mismatch

RoleBinding hoặc ClusterRoleBinding sai scope hoặc subject.

### request mismatch

Sai:

* verb
* resource
* apiGroup
* subresource

### token / identity issue

Ví dụ:

* token hết hạn
* sai context
* token không mount

### namespace vs cluster scope

Nhầm phạm vi permission.

---

## 2. Symptom → hướng xử lý

### Forbidden: User "<...>" cannot ...

#### Nghĩ ngay

RBAC deny.

#### Check trước

```bash
kubectl auth can-i
```

và parse:

* verb
* resource
* subresource

#### Phân biệt với

* app-level 403
* admission reject

---

### Unauthorized / 401

#### Nghĩ ngay

Authn fail.

Ví dụ:

* token thiếu
* token sai
* token hết hạn

#### Check trước

* ServiceAccount token mount
* automount

#### Phân biệt với

403 (authz).

---

### pod gọi API fail nhưng kubectl OK

#### Nghĩ ngay

Khác identity.

Ví dụ:

* user
* service account

#### Check trước

```text
spec.serviceAccountName
```

#### Phân biệt với

Network issue.

---

### SA có role nhưng vẫn bị deny

#### Nghĩ ngay

Binding sai namespace hoặc sai scope.

#### Check trước

* RoleBinding
* ClusterRoleBinding

#### Phân biệt với

request mismatch.

---

### chỉ fail ở 1 namespace

#### Nghĩ ngay

RoleBinding sai namespace.

#### Check trước

Binding đang nằm ở namespace nào.

#### Phân biệt với

cluster resource.

---

### fail ở cluster-scope resource

Ví dụ:

* nodes
* namespaces

#### Nghĩ ngay

Thiếu ClusterRoleBinding.

#### Check trước

Resource có phải namespaced resource không.

#### Phân biệt với

RoleBinding.

---

### kubectl auth can-i --as fail

#### Nghĩ ngay

Thiếu quyền impersonate.

#### Check trước

RBAC của chính user.

#### Phân biệt với

quyền của target ServiceAccount.

---

## 3. Playbook nhanh

### Bước 1

Xác định loại lỗi.

* timeout → không phải RBAC
* TLS → không phải RBAC
* 401 → authn
* 403 → authz hoặc admission

---

### Bước 2

Xác định identity.

User:

```bash
kubectl auth whoami
```

Pod:

```text
serviceAccountName
```

---

### Bước 3

Reconstruct request.

Xác định:

* verb
* resource
* apiGroup
* subresource
* namespace

---

### Bước 4

Verify RBAC.

* kubectl auth can-i
* RoleBinding
* ClusterRoleBinding
* namespace scope
* cluster scope

---

## 4. Common mismatches

* serviceAccountName != ServiceAccount mong muốn
* ServiceAccount cùng tên nhưng khác namespace
* RoleBinding đặt sai namespace
* RoleBinding dùng cho cluster-scope resource
* thiếu ClusterRoleBinding
* subresource mismatch (pods/log, exec, scale)
* verb mismatch (get vs list vs watch)
* apiGroup mismatch
* token không mount (automount=false)
* token expired nhưng app không reload
* impersonation không có quyền

---

## 5. Mental shortcuts

* Forbidden + User "<...>" → RBAC
* 401 Unauthorized → authn/token
* kubectl OK, pod fail → khác identity
* chỉ fail 1 namespace → binding sai namespace
* chỉ fail cluster resource → thiếu ClusterRoleBinding
* can-i OK nhưng vẫn fail → admission
* cannot impersonate → lỗi ở bạn, không phải target
* fail sau ~1h → token rotation/app caching

---

## 6. Lệnh / tín hiệu cần xem đầu tiên

* `kubectl auth whoami`
* `kubectl auth can-i <verb> <resource>`
* `kubectl auth can-i --as=system:serviceaccount:<ns>:<sa>`
* `kubectl get pod -o yaml`
* `kubectl api-resources`
* `kubectl create token <sa>`
* `kubectl --v=7`

---

## 7. Nhầm lẫn phổ biến

* RBAC 403 vs app-level 403
* authn vs authz (401 vs 403)
* RoleBinding vs ClusterRoleBinding
* RoleBinding dùng cho cluster resource
* service account vs kubeconfig user
* token Secret vs projected token
* nghĩ RBAC có deny rule (thực tế không có)
* impersonation là client-side (thực tế server validate)
