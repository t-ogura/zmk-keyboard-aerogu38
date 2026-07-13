# Aerogu
現在テスター向けに販売しているAeroguのファームウェア置き場

## ファームウェアのビルド

### GitHub Actions

このリポジトリへ push すると
[.github/workflows/build.yml](.github/workflows/build.yml) が自動的に
[`build.yaml`](build.yaml) の全エントリをマトリクスビルドします。
GitHub Actions の Artifacts から `firmware` をダウンロードしてください。

ビルドターゲット:

| Artifact | 内容 |
|---|---|
| `aerogu38_right_prospector.uf2` | 右 (セントラル)、Prospector 有効 |
| `aerogu38_right.uf2` | 右 (セントラル)、Prospector 無効 |
| `aerogu38_left.uf2` | 左 (ペリフェラル) |
| `settings_reset.uf2` | BLE ペアリング情報リセット用 |


## 書き込み (フラッシュ)

1. USB ケーブルでマイコンを PC に接続
2. リセットボタンを **2 回素早く** 押すと `XIAO-SENSE` または `XIAO-BLE` という
   USB ドライブとして認識される (DFU モード)
3. 対応する `.uf2` をドラッグ&ドロップ
4. 自動再起動して反映

新しい構成に切り替える際 (例: 別バリアントへ移行、GATT 構造が変わった等) は、
先に `settings_reset.uf2` を両側に書いて BLE ペアリング情報をクリアすると安全。

## 設定変更 (DYA Studio)

`aerogu38_right_prospector.uf2` または `aerogu38_right.uf2` どちらでも
DYA Studio 経由でランタイム設定が可能:

ただし、Prospector Scanner版は有線接続のみ対応

1. Chrome で [DYA Studio](https://studio.dya.cormoran.works/) を開く
2. USB を選択してAeroguを選ぶ
3. トラックボール感度、自動マウスレイヤー、idle/sleep タイムアウトなどを編集
4. 保存すると nRF52840 の settings 領域に persistent 保存される

## 依存モジュール / ライセンス

このプロジェクトは [MIT License](LICENSE) で配布されます (`Copyright (c) 2026 Tadashi Ogura`)。
ビルドに必要な外部依存とそのライセンスは以下の通りです。すべてビルド時に
[`config/west.yml`](config/west.yml) 経由で取得されるため本リポジトリ内では
再配布していませんが、謝辞および注意点として明示します。

| Module | License | Origin |
|---|---|---|
| [ZMK firmware (cormoran fork)](https://github.com/cormoran/zmk) | MIT | The ZMK Contributors |
| [prospector-zmk-module](https://github.com/carrefinho/prospector-zmk-module) | MIT | carrefinho 2024 + Prospector ZMK Module Contributors 2025 |
| [zmk-driver-paw3222](https://github.com/sekigon-gonnoc/zmk-driver-paw3222) | **Apache 2.0** | Google LLC 2024 + sekigon-gonnoc 2025 (modifications) |
| [zmk-rgbled-widget](https://github.com/caksoylar/zmk-rgbled-widget) | MIT | Cem Aksoylar 2023 |
| [zmk-module-ble-management](https://github.com/cormoran/zmk-module-ble-management) | MIT | cormoran 2026 |
| [zmk-module-battery-history](https://github.com/cormoran/zmk-module-battery-history) | MIT | cormoran 2026 |
| [zmk-module-settings-rpc](https://github.com/cormoran/zmk-module-settings-rpc) | MIT | cormoran 2026 |
| [zmk-module-runtime-input-processor](https://github.com/cormoran/zmk-module-runtime-input-processor) | MIT | cormoran 2026 |
| [zmk-input-processor-deadzone](https://github.com/t-ogura/zmk-input-processor-deadzone) | MIT | Tadashi Ogura 2026 |

### ライセンス上の注意点

- **paw3222 ドライバは Apache 2.0** であり、本リポジトリ (MIT) とライセンスが異なります。
  Apache 2.0 は MIT と互換 (MIT プロジェクトに取り込み可能) ですが、
  使用にあたって元の著作権表示と LICENSE 全文の保持が必要です。
  上記表での明示と、`west update` 時にモジュールに同梱される `LICENSE` ファイルが
  これに該当します。
- 他の依存はすべて MIT で、上記表での出自明示で十分です。
- Apache 2.0 / MIT 双方の本文と互換性については以下を参照:
  - <https://www.apache.org/licenses/LICENSE-2.0>
  - <https://opensource.org/license/mit>
  - <https://www.apache.org/licenses/GPL-compatibility.html>

## 既知の制限

### DYA Studio BLE 経由の接続が動作しない

Prospector 有効バリアント (`aerogu38_right_prospector.uf2`) で、
Web Bluetooth 経由の DYA Studio セッションが確立できません。
USB 接続なら問題ありません。

技術的な背景: Prospector v2.2.x は legacy advertising API を使用しているため、
ZMK Studio の directed advertising と単一の advertising slot を取り合います。
Prospector を完全無効化したい場合は `aerogu38_right.uf2` を使用してください。

## 参考実装・参照リンク

- [ZMK firmware](https://zmk.dev) — 本体ドキュメント、Behavior 一覧、Build instructions
- [urob/zmk-config](https://github.com/urob/zmk-config) — Justfile + Nix によるビルド環境のベース
- [DYA Studio 統合ガイド](https://github.com/cormoran/zmk-keyboard-dya-dash) — cormoran 氏のリファレンス実装
- [DYA Studio](https://studio.dya.cormoran.works/) — ブラウザベースの ZMK Studio 拡張
- [Prospector ZMK Module](https://github.com/carrefinho/prospector-zmk-module) — Status advertisement

## ライセンス

[MIT License](LICENSE) — Copyright (c) 2026 Tadashi Ogura
