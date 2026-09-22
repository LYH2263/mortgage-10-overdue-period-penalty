<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const rules = ref([])
const editingId = ref(null)
const form = ref({ name: '', grace_days: 0, daily_rate: 0.05, enabled: true })
const error = ref('')

const reset = () => { editingId.value = null; form.value = { name: '', grace_days: 0, daily_rate: 0.05, enabled: true } }
const load = async () => { rules.value = (await getJSON('/api/penalty-rules')).items }
const save = async () => {
  error.value = ''
  try {
    if (editingId.value) await putJSON(`/api/penalty-rules/${editingId.value}`, form.value)
    else await postJSON('/api/penalty-rules', form.value)
    reset(); await load()
  } catch (e) { error.value = String(e) }
}
const edit = (r) => {
  editingId.value = r.id
  form.value = { name: r.name, grace_days: r.grace_days, daily_rate: r.daily_rate, enabled: !!r.enabled }
}
const disable = async (r) => { await postJSON(`/api/penalty-rules/${r.id}/disable`, {}); await load() }
onMounted(load)
</script>
<template><div class="page"><h1>利率说明</h1><p>默认等额本息：月利率 = 年利率 / 12 / 100。</p>
<h2>逾期罚息规则</h2>
<p>罚息 = 逾期期月供 × 日罚率 × 超出免罚的天数；测算命中启用规则时计入。</p>
<table>
  <tr><th>#</th><th>名称</th><th>免罚天数</th><th>日罚率%/日</th><th>状态</th><th></th></tr>
  <tr v-for="r in rules" :key="r.id">
    <td>{{ r.id }}</td><td>{{ r.name }}</td><td>{{ r.grace_days }}</td><td>{{ r.daily_rate }}</td>
    <td>{{ r.enabled ? '启用' : '停用' }}</td>
    <td><button @click="edit(r)">编辑</button> <button v-if="r.enabled" @click="disable(r)">停用</button></td>
  </tr>
</table>
<h3>{{ editingId ? `编辑规则 #${editingId}` : '新建规则' }}</h3>
<label>名称 <input v-model="form.name" placeholder="罚息规则" /></label>
<label>免罚天数 <input type="number" v-model.number="form.grace_days" min="0" /></label>
<label>日罚率%/日 <input type="number" step="0.001" v-model.number="form.daily_rate" min="0" /></label>
<label>启用 <input type="checkbox" v-model="form.enabled" /></label>
<button @click="save">{{ editingId ? '保存' : '创建' }}</button>
<button v-if="editingId" @click="reset">取消</button>
<p v-if="error" class="error">{{ error }}</p>
</div></template>
