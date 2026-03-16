#!/usr/bin/env node
/**
 * 将 resources/icon.png 复制到 Android 各 mipmap 目录作为应用图标
 * 无需 sharp，直接复制（系统会缩放）
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const src = path.join(root, 'resources', 'icon.png')
const androidRes = path.join(root, 'android', 'app', 'src', 'main', 'res')

const mipmaps = [
  'mipmap-mdpi',
  'mipmap-hdpi',
  'mipmap-xhdpi',
  'mipmap-xxhdpi',
  'mipmap-xxxhdpi',
]

if (!fs.existsSync(src)) {
  console.error('未找到 resources/icon.png，请先放入图标文件')
  process.exit(1)
}

for (const dir of mipmaps) {
  const destDir = path.join(androidRes, dir)
  if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true })
  for (const name of ['ic_launcher.png', 'ic_launcher_round.png', 'ic_launcher_foreground.png']) {
    const dest = path.join(destDir, name)
    fs.copyFileSync(src, dest)
    console.log('已写入:', dest)
  }
}

console.log('图标生成完成')
