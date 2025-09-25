import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import mysql from 'mysql2/promise'

dotenv.config()
const app = express()
app.use(cors())
app.use(express.json())

// MySQL 커넥션 풀 설정
const pool = mysql.createPool({
  host:     process.env.DB_HOST,
  port:     process.env.DB_PORT,
  user:     process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
})

// 1) 전체 디바이스 목록
app.get('/api/devices', async (req, res) => {
  const [rows] = await pool.query(`
    SELECT device_id, device_name, device_type, description
    FROM device
    ORDER BY device_id
  `)
  res.json(rows)
})

// 2) 전체 최신 이벤트 (limit=100)
app.get('/api/events', async (req, res) => {
  const [rows] = await pool.query(`
    SELECT e.event_id, e.device_id, d.device_name, e.event_time, e.event_type, e.note
    FROM event e
    JOIN device d ON e.device_id = d.device_id
    ORDER BY e.event_time DESC
    LIMIT 100
  `)
  res.json(rows)
})

// 3) 전체 최신 센서 리딩 (limit=100)
app.get('/api/readings', async (req, res) => {
  const [rows] = await pool.query(`
    SELECT r.reading_id, r.device_id, d.device_name,
           r.metric, r.reading_time, r.value_float, r.threshold, r.unit
    FROM sensor_reading r
    JOIN device d ON r.device_id = d.device_id
    ORDER BY r.reading_time DESC
    LIMIT 100
  `)
  res.json(rows)
})

// 4) 특정 디바이스의 메타 정보
app.get('/api/devices/:deviceId', async (req, res) => {
  const { deviceId } = req.params
  const [rows] = await pool.query(
    `SELECT device_id, device_name, device_type, description
     FROM device
     WHERE device_id = ?`,
    [deviceId]
  )
  if (rows.length === 0) {
    return res.status(404).json({ error: 'Device not found' })
  }
  res.json(rows[0])
})

// 5) 특정 디바이스의 센서 리딩 (최근 100개)
app.get('/api/devices/:deviceId/readings', async (req, res) => {
  const { deviceId } = req.params
  const limit = parseInt(req.query.limit) || 100
  const [rows] = await pool.query(
    `SELECT reading_id, reading_time, metric, value_float, threshold, unit
     FROM sensor_reading
     WHERE device_id = ?
     ORDER BY reading_time DESC
     LIMIT ?`,
    [deviceId, limit]
  )
  res.json(rows.reverse())  // 시간 오름차순으로 보고 싶으면 reverse
})

// 6) 특정 디바이스의 이벤트 목록 (최근 100개)
app.get('/api/devices/:deviceId/events', async (req, res) => {
  const { deviceId } = req.params
  const limit = parseInt(req.query.limit) || 100
  const [rows] = await pool.query(
    `SELECT event_id, event_time, event_type, note
     FROM event
     WHERE device_id = ?
     ORDER BY event_time DESC
     LIMIT ?`,
    [deviceId, limit]
  )
  res.json(rows.reverse())
})

// 7) 특정 디바이스의 이벤트 타입별 카운트
app.get('/api/devices/:deviceId/events/count-by-type', async (req, res) => {
  const { deviceId } = req.params
  const [rows] = await pool.query(
    `SELECT event_type AS type, COUNT(*) AS count
     FROM event
     WHERE device_id = ?
     GROUP BY event_type`,
    [deviceId]
  )
  // { power_on: 3, pick_up: 5, ... } 형태로 변환
  const result = {}
  rows.forEach(r => { result[r.type] = r.count })
  res.json(result)
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`)
})
