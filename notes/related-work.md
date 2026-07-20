# Related work（調査メモ）

Phase 2–4 で調査・執筆．各項目は「何と比較し，何が差分か」を一行で書けるまで調べる．
確定した比較は claims/contribution-map.md の baseline 列へ．

## 調査すべき領域

1. **解析学・PDE の大規模形式化**
   - mathlib における測度論・関数解析・Sobolev 空間の既存範囲
   - 他証明支援系（Coq/Isabelle）での流体方程式・発展方程式の形式化の有無
2. **AI 支援定理証明・形式化**
   - LLM による証明生成（自動 tactic，whole-proof generation）との違い
     （本件は agent-orchestrated *development*，証明探索ベンチマークではない）
3. **AI エージェントによるソフトウェア開発の実証研究**
   - multi-agent orchestration，役割分離，検証ゲートに関する報告
4. **proof engineering / 形式化プロジェクトの工程管理**
   - 大規模形式化プロジェクト（odd order theorem，Liquid Tensor Experiment 等）の
     工程・検証体制の記録

## メモ

（追記していく．出典は必ず URL / DOI 付きで）
