# HABITAT_FUSION_STRUCTURAL_REPORT_Ω

- **Doctrine**: P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · Phase 3 permanent
- **Emitted at**: 2026-06-12T13:07:35.812209+00:00
- **Cadence**: toutes les 24h

---

```
══════════════════════════════════════════════════════════════════════════════
  HABITAT_FUSION_STRUCTURAL_REPORT_Ω · 2026-06-12T13:07:35.765095+00:00
══════════════════════════════════════════════════════════════════════════════

§ A · ENGINE P0
  HABITAT-FUSION-ENGINE-P0 · vV1-PRE-FUSION-2026-05
  Phase           : P0_PRE_FUSION
  Status global   : STRUCTURAL_ACTIVATED_PRE_INGESTION
  Axes ready/total: 2/4 · pre_ingestion=2
  weight_active_p0: 0.35
  completion_ratio: 0.35

§ B · ENGINE P1 STRUCTURAL+
  HABITAT-FUSION-ENGINE-P1 · vV1.0-STRUCTURAL_PLUS-AWAITING-CREDENTIALS
  Phase                   : P1_STRUCTURAL+_AWAITING_INGESTION
  weight_active           : 0.35 (INCHANGÉ vs P0)
  ingestion_p1_ready      : True
  clients credential ready: 4/4
  clients armés           : 4/4

§ C · CLIENTS INGESTION (CODE-READY · INERTES)
  nasa_hls                 : mode=INGESTION_READY · cred_ready=True
  esa_sentinel2_l2a        : mode=INGESTION_READY · cred_ready=True
  nrcan_hrdem              : mode=INGESTION_READY · cred_ready=True
  mffp_foret_ouverte       : mode=INGESTION_READY · cred_ready=True

§ D · COMPUTE VALIDATION @ BSL (48.21, -68.38)
  Divergence biologique stricte: True
  Distinct par saison: {'printemps': 5, 'ete': 5, 'automne': 5, 'hiver': 5}
  Sample scores      :
    chevreuil_printemps           : 35.2
    orignal_printemps             : 63.6
    ours_noir_printemps           : 71.4
    coyote_printemps              : 52.2
    dindon_sauvage_printemps      : 7.1
    chevreuil_ete                 : 36.7
    orignal_ete                   : 62.3
    ours_noir_ete                 : 63.2
    ... (20 total)

§ E · VERROU PHASE III
  verrou_phase_iii  : True
  lecture_seule     : True
  weight_target_p2  : 1.0
  _note             : weight_active=0.35 INCHANGÉ · 2/4 axes effectifs · Clients NDVI/LiDAR CODE-READY mais INERTES (anti-générique strict).
══════════════════════════════════════════════════════════════════════════════

```
