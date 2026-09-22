<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
function parse(h) {
  try { return { ...h, input: JSON.parse(h.input_json), result: JSON.parse(h.result_json) } }
  catch { return { ...h, input: {}, result: {} } }
}
onMounted(async () => {
  const raw = (await getJSON('/api/history')).items
  items.value = raw.map(parse)
})
</script>
<template><div class="page">
  <h1>试算记录</h1>
  <table>
    <thead>
      <tr><th>#</th><th>时间</th><th>类型</th><th>原月供</th><th>罚息</th><th>含罚合计</th></tr>
    </thead>
    <tbody>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td>
        <td>{{ h.created_at }}</td>
        <td>{{ h.kind }}</td>
        <td>{{ h.result.penalty ? h.result.penalty.base_monthly_payment : '—' }}</td>
        <td>{{ h.result.penalty ? h.result.penalty.penalty : '—' }}</td>
        <td>{{ h.result.penalty ? h.result.penalty.payment_with_penalty : '—' }}</td>
      </tr>
    </tbody>
  </table>
  <p class="muted">罚息为写入时的固化快照，后续调整日罚率不影响历史记录。</p>
</div></template>
<style scoped>
.muted { color:#6b5d48; }
</style>
