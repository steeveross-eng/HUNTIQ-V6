import React from 'react';

/**
 * STEVE-MAX P5: Amenagement Report Panel
 * Shows the complete 2km square setup analysis:
 * saline, cache, feeding site, wind analysis, path, action plan
 */
const AmenagementPanel = ({ report, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e] animate-pulse" data-testid="amenagement-loading">
        <div className="h-3 bg-gray-800 rounded w-3/4 mb-2" />
        <div className="h-2 bg-gray-800 rounded w-1/2" />
      </div>
    );
  }

  if (!report || !report.sections) return null;

  const s = report.sections;

  return (
    <div className="space-y-2" data-testid="amenagement-panel">
      <div className="text-[10px] text-amber-400 uppercase tracking-wider font-bold">
        Amenagement 2km
      </div>

      {/* Saline */}
      {s['1_saline'] && (
        <ReportSection
          title={s['1_saline'].title}
          detail={s['1_saline'].justification}
          priority={s['1_saline'].priority}
          icon="droplet"
          testId="amenagement-saline"
        />
      )}

      {/* Cache */}
      {s['3_cache'] && (
        <ReportSection
          title={s['3_cache'].title}
          detail={s['3_cache'].justification}
          priority={s['3_cache'].priority}
          icon="eye"
          testId="amenagement-cache"
        />
      )}

      {/* ALIMENTATION-V2: "Alimentation secondaire" SUPPRIME — directive STEEVE-MAX */}

      {/* Trajet */}
      {s['4_trajet_optimal'] && (
        <div className="bg-[#0d0d14] rounded p-2 border border-[#1a1a2e]" data-testid="amenagement-trajet">
          <div className="text-[9px] text-orange-400 font-bold mb-1">Trajet optimal</div>
          <div className="text-[9px] text-gray-400">
            {s['4_trajet_optimal'].distance_km} km | {s['4_trajet_optimal'].zones_visited} zones
          </div>
          <div className="text-[8px] text-gray-500 mt-0.5">{s['4_trajet_optimal'].strategy}</div>
        </div>
      )}

      {/* Vents */}
      {s['5_vents_dominants'] && (
        <div className="bg-[#0d0d14] rounded p-2 border border-[#1a1a2e]" data-testid="amenagement-vents">
          <div className="text-[9px] text-cyan-400 font-bold mb-1">Vents dominants</div>
          <div className="flex items-center gap-2 text-[9px] text-gray-400">
            <span>{s['5_vents_dominants'].direction_cardinal} ({s['5_vents_dominants'].direction_deg}°)</span>
            <span>{s['5_vents_dominants'].vitesse_kmh} km/h</span>
            <span className="text-green-400">{s['5_vents_dominants'].qualite}</span>
          </div>
          <div className="text-[8px] text-gray-500 mt-0.5">{s['5_vents_dominants'].approche_recommandee}</div>
        </div>
      )}

      {/* Plan d'action */}
      {s['8_plan_action'] && (
        <div className="bg-[#0d0d14] rounded p-2 border border-[#1a1a2e]" data-testid="amenagement-plan">
          <div className="text-[9px] text-red-400 font-bold mb-1">
            Plan d'action (confiance: {s['8_plan_action'].score_confiance}%)
          </div>
          <div className="space-y-0.5">
            {(s['8_plan_action'].etapes || []).map((step, i) => (
              <div key={i} className="text-[8px] text-gray-500 flex gap-1">
                <span className="text-amber-400 flex-shrink-0">{i + 1}.</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const ReportSection = ({ title, detail, priority, testId }) => (
  <div className="bg-[#0d0d14] rounded p-2 border border-[#1a1a2e]" data-testid={testId}>
    <div className="flex items-center gap-1">
      <span className={`text-[9px] font-bold ${priority === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`}>
        {title}
      </span>
    </div>
    <div className="text-[8px] text-gray-500 mt-0.5">{detail || 'N/A'}</div>
  </div>
);

export default AmenagementPanel;
