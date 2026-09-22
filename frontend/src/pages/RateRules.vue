<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const items = ref([])
const err = ref('')
const form = ref({ name: '', grace_days: 3, daily_rate: 0.0005, enabled: true })

async function load() {
  err.value = ''
  try { items.value = (await getJSON('/api/penalty-rules')).items }
  catch (e) { err.value = String(e.message || e) }
}
async function createRule() {
  err.value = ''
  try {
    await postJSON('/api/penalty-rules', {
      name: form.value.name,
      grace_days: Number(form.value.grace_days),
      daily_rate: Number(form.value.daily_rate),
      enabled: !!form.value.enabled,
    })
    form.value = { name: '', grace_days: 3, daily_rate: 0.0005, enabled: true }
    await load()
  } catch (e) { err.value = String(e.message || e) }
}
async function save(r) {
  err.value = ''
  try {
    await putJSON(`/api/penalty-rules/${r.id}`, {
      name: r.name,
      grace_days: Number(r.grace_days),
      daily_rate: Number(r.daily_rate),
      enabled: !!r.enabled,
    })
    await load()
  } catch (e) { err.value = String(e.message || e) }
}
async function toggle(r) {
  err.value = ''
  try {
    if (r.enabled) {
      await postJSON(`/api/penalty-rules/${r.id}/disable`, {})
    } else {
      await putJSON(`/api/penalty-rules/${r.id}`, { enabled: true })
    }
    await load()
  } catch (e) { err.value = String(e.message || e) }
}

onMounted(load)
</script>
<template>
  <div class="page">
    <h1>逾期罚息规则</h1>
    <p class="hint">罚息 = 该期月供 × 日罚率 × 超出免罚天数的天数。仅启用规则参与试算命中。</p>
    <p v-if="err" class="err">{{ err }}</p>

    <table>
      <thead>
        <tr><th>#</th><th>名称</th><th>免罚天数</th><th>日罚率</th><th>启用</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="r in items" :key="r.id" :class="{ off: !r.enabled }">
          <td>{{ r.id }}</td>
          <td><input v-model="r.name" /></td>
          <td><input v-model.number="r.grace_days" type="number" min="0" style="width:80px" /></td>
          <td><input v-model.number="r.daily_rate" type="number" step="0.0001" min="0" style="width:110px" /></td>
          <td>{{ r.enabled ? '启用' : '停用' }}</td>
          <td>
            <button @click="save(r)">保存</button>
            <button @click="toggle(r)">{{ r.enabled ? '停用' : '启用' }}</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h2>新增规则</h2>
    <div class="form-row">
      <label>名称 <input v-model="form.name" placeholder="规则名称" /></label>
      <label>免罚天数 <input v-model.number="form.grace_days" type="number" min="0" /></label>
      <label>日罚率 <input v-model.number="form.daily_rate" type="number" step="0.0001" min="0" /></label>
      <label class="chk"><input type="checkbox" v-model="form.enabled" /> 启用</label>
      <button @click="createRule">创建</button>
    </div>
  </div>
</template>
<style scoped>
.hint { color:#6b5d48; }
.err { color:#a11; }
.off td { opacity:.55; }
.form-row { display:flex; gap:1rem; align-items:center; flex-wrap:wrap; margin-top:.5rem; }
.chk { display:flex; align-items:center; gap:.3rem; }
button + button { margin-left:.4rem; }
</style>
