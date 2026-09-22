<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => {
  items.value = (await getJSON('/api/history')).items.map(h => ({
    ...h,
    input: JSON.parse(h.input_json || '{}'),
    result: JSON.parse(h.result_json || '{}'),
  }))
})
</script>
<template><div class="page"><h1>试算记录</h1>
<table>
  <tr><th>#</th><th>时间</th><th>月供</th><th>逾期</th><th>罚息</th><th>含罚合计</th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>#{{ h.id }}</td>
    <td>{{ h.created_at }}</td>
    <td>{{ h.result.monthly_payment }}</td>
    <td>{{ h.result.penalty && h.result.penalty.period ? `第${h.result.penalty.period}期 ${h.result.penalty.days}天` : '-' }}</td>
    <td>{{ h.result.penalty ? h.result.penalty.penalty : '-' }}</td>
    <td>{{ h.result.penalty ? h.result.penalty.payment_with_penalty : '-' }}</td>
  </tr>
</table>
</div></template>
