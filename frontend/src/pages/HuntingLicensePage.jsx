/**
 * HuntingLicensePage - Module "Permis de chasse" avec dropdown dynamique
 * ═══════════════════════════════════════════════════════════════════════════════
 * DIRECTIVE COPILOT MAÎTRE: Système Pays → Province/État → Redirection portail officiel
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useMemo } from 'react';
import { ExternalLink, ChevronDown, MapPin, FileText, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { GlobalContainer } from '@/core/layouts';

// ═══════════════════════════════════════════════════════════════════════════════
// MAPPING COMPLET DES PORTAILS OFFICIELS
// ═══════════════════════════════════════════════════════════════════════════════

const HUNTING_LICENSE_DATA = {
  canada: {
    label: "Canada",
    flag: "🇨🇦",
    regions: [
      { id: "qc", name: "Québec", url: "https://www.quebec.ca/tourisme-loisirs-sport/activites-sportives-et-de-plein-air/chasse-sportive/permis-certificat/acheter-permis" },
      { id: "on", name: "Ontario", url: "https://www.huntandfishontario.com" },
      { id: "on-nr", name: "Ontario (non-résidents)", url: "https://www.ontario.ca/page/hunting-licence-non-residents" },
      { id: "sk", name: "Saskatchewan", url: "https://hal.saskatchewan.ca" },
      { id: "ab", name: "Alberta", url: "https://www.albertarelm.com" },
      { id: "bc", name: "British Columbia", url: "https://www2.gov.bc.ca/gov/content/sports-culture/recreation/fishing-hunting/hunting" },
      { id: "mb", name: "Manitoba", url: "https://www.manitobaelicensing.ca" },
      { id: "nb", name: "New Brunswick", url: "https://www.gnb.ca/naturalresources" },
      { id: "ns", name: "Nova Scotia", url: "https://www.hmc.gov.ns.ca" },
      { id: "pe", name: "Prince Edward Island", url: "https://www.princeedwardisland.ca/en/topic/hunting-and-fishing" },
      { id: "nl", name: "Newfoundland & Labrador", url: "https://www.gov.nl.ca/ffa/wildlife/hunting" },
      { id: "yt", name: "Yukon", url: "https://yukon.ca/en/hunting-licences-permits" },
      { id: "nt", name: "Northwest Territories", url: "https://www.enr.gov.nt.ca" },
      { id: "nu", name: "Nunavut", url: "https://www.gov.nu.ca" },
    ]
  },
  usa: {
    label: "États-Unis",
    flag: "🇺🇸",
    regions: [
      { id: "al", name: "Alabama", url: "https://www.outdooralabama.com" },
      { id: "ak", name: "Alaska", url: "https://www.adfg.alaska.gov/store" },
      { id: "az", name: "Arizona", url: "https://license.azgfd.gov" },
      { id: "ar", name: "Arkansas", url: "https://www.agfc.com" },
      { id: "ca", name: "California", url: "https://wildlife.ca.gov/Licensing/Online-Sales" },
      { id: "co", name: "Colorado", url: "https://cpw.state.co.us/buyapply" },
      { id: "ct", name: "Connecticut", url: "https://portal.ct.gov/DEEP" },
      { id: "de", name: "Delaware", url: "https://dnrec.alpha.delaware.gov" },
      { id: "fl", name: "Florida", url: "https://gooutdoorsflorida.com" },
      { id: "ga", name: "Georgia", url: "https://gooutdoorsgeorgia.com" },
      { id: "hi", name: "Hawaii", url: "https://dlnr.hawaii.gov" },
      { id: "id", name: "Idaho", url: "https://idfg.idaho.gov/buy" },
      { id: "il", name: "Illinois", url: "https://www.exploremoreil.com" },
      { id: "in", name: "Indiana", url: "https://www.in.gov/dnr" },
      { id: "ia", name: "Iowa", url: "https://gooutdoorsiowa.com" },
      { id: "ks", name: "Kansas", url: "https://ksoutdoors.com" },
      { id: "ky", name: "Kentucky", url: "https://fw.ky.gov" },
      { id: "la", name: "Louisiana", url: "https://www.wlf.louisiana.gov" },
      { id: "me", name: "Maine", url: "https://www.maine.gov/ifw" },
      { id: "md", name: "Maryland", url: "https://compass.dnr.maryland.gov" },
      { id: "ma", name: "Massachusetts", url: "https://massfishhunt.mass.gov" },
      { id: "mi", name: "Michigan", url: "https://www.mdnr-elicense.com" },
      { id: "mn", name: "Minnesota", url: "https://www.dnr.state.mn.us" },
      { id: "ms", name: "Mississippi", url: "https://www.mdwfp.com" },
      { id: "mo", name: "Missouri", url: "https://mdc.mo.gov" },
      { id: "mt", name: "Montana", url: "https://ols.fwp.mt.gov" },
      { id: "ne", name: "Nebraska", url: "https://ngpc-home.ne.gov" },
      { id: "nv", name: "Nevada", url: "https://www.ndow.org" },
      { id: "nh", name: "New Hampshire", url: "https://www.wildlife.state.nh.us" },
      { id: "nj", name: "New Jersey", url: "https://www.njfishandwildlife.com" },
      { id: "nm", name: "New Mexico", url: "https://onlinesales.wildlife.state.nm.us" },
      { id: "ny", name: "New York", url: "https://decals.licensing.east.kalkomey.com" },
      { id: "nc", name: "North Carolina", url: "https://www.ncwildlife.org" },
      { id: "nd", name: "North Dakota", url: "https://gf.nd.gov" },
      { id: "oh", name: "Ohio", url: "https://oh-web.s3licensing.com" },
      { id: "ok", name: "Oklahoma", url: "https://www.wildlifedepartment.com" },
      { id: "or", name: "Oregon", url: "https://odfw.huntfishoregon.com" },
      { id: "pa", name: "Pennsylvania", url: "https://huntfish.pa.gov" },
      { id: "ri", name: "Rhode Island", url: "https://www.ri.gov/dem/huntfish" },
      { id: "sc", name: "South Carolina", url: "https://www.dnr.sc.gov" },
      { id: "sd", name: "South Dakota", url: "https://gfp.sd.gov" },
      { id: "tn", name: "Tennessee", url: "https://www.gooutdoorstennessee.com" },
      { id: "tx", name: "Texas", url: "https://tpwd.texas.gov/business/licenses/online_sales" },
      { id: "ut", name: "Utah", url: "https://wildlife.utah.gov" },
      { id: "vt", name: "Vermont", url: "https://vtfishandwildlife.com" },
      { id: "va", name: "Virginia", url: "https://gooutdoorsvirginia.com" },
      { id: "wa", name: "Washington", url: "https://fishhunt.dfw.wa.gov" },
      { id: "wv", name: "West Virginia", url: "https://www.wvhunt.com" },
      { id: "wi", name: "Wisconsin", url: "https://gowild.wi.gov" },
      { id: "wy", name: "Wyoming", url: "https://wgfd.wyo.gov/apply-or-buy" },
    ]
  }
};

const HuntingLicensePage = () => {
  const [selectedCountry, setSelectedCountry] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("");

  // Régions disponibles selon le pays sélectionné
  const availableRegions = useMemo(() => {
    if (!selectedCountry) return [];
    return HUNTING_LICENSE_DATA[selectedCountry]?.regions || [];
  }, [selectedCountry]);

  // URL du portail officiel selon la région sélectionnée
  const licenseUrl = useMemo(() => {
    if (!selectedCountry || !selectedRegion) return null;
    const region = availableRegions.find(r => r.id === selectedRegion);
    return region?.url || null;
  }, [selectedCountry, selectedRegion, availableRegions]);

  // Nom de la région sélectionnée
  const selectedRegionName = useMemo(() => {
    const region = availableRegions.find(r => r.id === selectedRegion);
    return region?.name || "";
  }, [selectedRegion, availableRegions]);

  // Reset la région quand le pays change
  const handleCountryChange = (value) => {
    setSelectedCountry(value);
    setSelectedRegion("");
  };

  // Ouvrir le portail officiel
  const handleBuyLicense = () => {
    if (licenseUrl) {
      window.open(licenseUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <GlobalContainer>
      <div className="min-h-[calc(100vh-64px)] py-8 px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#f5a623]/20 mb-4">
            <FileText className="h-8 w-8 text-[#f5a623]" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            Permis de chasse
          </h1>
          <p className="text-gray-400 max-w-xl mx-auto">
            Accédez directement au portail officiel de votre province ou État pour acheter votre permis de chasse en toute légalité.
          </p>
        </div>

        {/* Main Card */}
        <Card className="max-w-xl mx-auto bg-gray-900/50 border-gray-800" data-testid="hunting-license-card">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-xl text-white flex items-center justify-center gap-2">
              <MapPin className="h-5 w-5 text-[#f5a623]" />
              Sélectionnez votre localisation
            </CardTitle>
            <CardDescription className="text-gray-400">
              Choisissez votre pays et votre province/État
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6 pt-4">
            {/* Dropdown 1: Pays */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                Choisir mon pays
              </label>
              <Select 
                value={selectedCountry} 
                onValueChange={handleCountryChange}
                data-testid="country-select"
              >
                <SelectTrigger className="w-full bg-gray-800 border-gray-700 text-white h-12">
                  <SelectValue placeholder="Sélectionnez un pays" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {Object.entries(HUNTING_LICENSE_DATA).map(([key, data]) => (
                    <SelectItem 
                      key={key} 
                      value={key}
                      className="text-white hover:bg-gray-700 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <span>{data.flag}</span>
                        <span>{data.label}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Dropdown 2: Province/État (dynamique) */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                Choisir ma province / mon État
              </label>
              <Select 
                value={selectedRegion} 
                onValueChange={setSelectedRegion}
                disabled={!selectedCountry}
                data-testid="region-select"
              >
                <SelectTrigger 
                  className={`w-full h-12 ${
                    selectedCountry 
                      ? 'bg-gray-800 border-gray-700 text-white' 
                      : 'bg-gray-800/50 border-gray-700/50 text-gray-500'
                  }`}
                >
                  <SelectValue 
                    placeholder={
                      selectedCountry 
                        ? "Sélectionnez une province/État" 
                        : "Choisissez d'abord un pays"
                    } 
                  />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 max-h-[300px]">
                  {availableRegions.map((region) => (
                    <SelectItem 
                      key={region.id} 
                      value={region.id}
                      className="text-white hover:bg-gray-700 cursor-pointer"
                    >
                      {region.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* CTA Button */}
            <Button
              onClick={handleBuyLicense}
              disabled={!licenseUrl}
              className={`w-full h-14 text-lg font-semibold transition-all duration-300 ${
                licenseUrl
                  ? 'bg-[#f5a623] hover:bg-[#e09000] text-black shadow-lg shadow-[#f5a623]/20'
                  : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              }`}
              data-testid="buy-license-btn"
            >
              <ExternalLink className="h-5 w-5 mr-2" />
              {licenseUrl 
                ? `Acheter mon permis maintenant` 
                : 'Sélectionnez votre localisation'
              }
            </Button>

            {/* Info badge when selection complete */}
            {licenseUrl && (
              <div className="flex items-center justify-center gap-2 text-sm text-gray-400 bg-gray-800/50 rounded-lg py-3 px-4">
                <Shield className="h-4 w-4 text-green-500" />
                <span>
                  Redirection vers le portail officiel de <strong className="text-white">{selectedRegionName}</strong>
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Section */}
        <div className="max-w-xl mx-auto mt-8 text-center">
          <p className="text-xs text-gray-500">
            Les liens redirigent vers les sites gouvernementaux officiels. 
            BIONIC™ n'est pas responsable du contenu des sites externes.
          </p>
        </div>
      </div>
    </GlobalContainer>
  );
};

export default HuntingLicensePage;
