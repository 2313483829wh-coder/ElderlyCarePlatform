#!/usr/bin/env node
/**
 * 生成自签名证书（无域名时用），适用于 47.111.26.171
 * 输出到 deploy/certs/ 和 frontend/android/app/src/main/res/raw/
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { generate } from 'selfsigned'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..', '..')
const ip = process.env.SSL_IP || '47.111.26.171'

const attrs = [{ name: 'commonName', value: ip }]
const notAfter = new Date()
notAfter.setFullYear(notAfter.getFullYear() + 10)
const extensions = [
  { name: 'basicConstraints', cA: false },
  { name: 'keyUsage', digitalSignature: true, keyEncipherment: true },
  { name: 'extKeyUsage', serverAuth: true, clientAuth: true },
  { name: 'subjectAltName', altNames: [{ type: 7, ip }], critical: true },
]

const pems = await generate(attrs, { notAfterDate: notAfter, extensions })
const certPem = pems.cert
const keyPem = pems.private

const deployCerts = path.join(root, 'deploy', 'certs')
const androidRaw = path.join(root, 'frontend', 'android', 'app', 'src', 'main', 'res', 'raw')

fs.mkdirSync(deployCerts, { recursive: true })
fs.mkdirSync(androidRaw, { recursive: true })

fs.writeFileSync(path.join(deployCerts, 'fullchain.pem'), certPem)
fs.writeFileSync(path.join(deployCerts, 'privkey.pem'), keyPem)
fs.writeFileSync(path.join(androidRaw, 'server_crt'), certPem)

console.log('证书已生成:')
console.log('  deploy/certs/fullchain.pem, privkey.pem')
console.log('  frontend/android/app/src/main/res/raw/server_crt')
console.log('执行: docker compose -f docker-compose.yml -f deploy/docker-compose.https-self-signed.yml up -d frontend')
console.log('安全组放行 443，.env.production 改为 https://' + ip + '/api，重打 APK')
