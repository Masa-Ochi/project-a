from urllib.parse import urljoin, urlparse
# from robobrowser import RoboBrowser 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import sys
import json
import time
import timeout_decorator


# - Define driverd
# browser = RoboBrowser(parser='html.parser') 
args = sys.argv # [0]:from page / [1]:to page
cwd = os.getcwd()
driver_path = '/Users/masamitsuochiai/Documents/wk/files/chromedriver'
DOWNLOADED_URL_PATH = os.path.join(cwd, 'downloaded_url_list')
ERR_URL_PATH = os.path.join(cwd, 'err_url_list')
chromeOptions = webdriver.ChromeOptions()
prefs = {
	"download.default_directory" : os.path.join(cwd, 'sources_invest_csv'),
	"profile.default_content_setting_values.notifications" : 2
	}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)


def test_main():
	url = "https://jp.investing.com/"
	login(url)
	target_lst = [
		"https://jp.investing.com/etfs/proshares-short-msci-eafe",
		"https://jp.investing.com/etfs/flexshares-quality-div-def",
		"https://jp.investing.com/etfs/spdr-dj-stoxx-50",
		"https://jp.investing.com/etfs/ishares-russell-top-200-value",
		"https://jp.investing.com/etfs/direxion-daily-mid-cap-bear-3x",
		"https://jp.investing.com/etfs/pimco-inter.-mun.-bond-strategy",
		"https://jp.investing.com/etfs/spdr-nuveen-s-p-high-y-mun.-bond",
		"https://jp.investing.com/etfs/ishares-msci-peru",
		"https://jp.investing.com/etfs/wisdomtree-earnings-500-fund",
		"https://jp.investing.com/etfs/spdr-global-allocation",
		"https://jp.investing.com/etfs/ipath-pure-beta-coffee",
		"https://jp.investing.com/etfs/fidelity-msci-telecom-svcs",
		"https://jp.investing.com/etfs/powersh.-dynamic-food---beverage",
		"https://jp.investing.com/etfs/global-x-gold-explorers",
		"https://jp.investing.com/etfs/egshares-india-infrastructure",
		"https://jp.investing.com/etfs/proshares-ultrashort-semicon.",
		"https://jp.investing.com/etfs/ishares-msci-colombia-capped",
		"https://jp.investing.com/etfs/proshares-ultrashort-yen",
		"https://jp.investing.com/etfs/powersh-wilderhill-clean-energy",
		"https://jp.investing.com/etfs/ishares-kld-select-social-index",
		"https://jp.investing.com/etfs/ishares-msci-world",
		"https://jp.investing.com/etfs/ishares-gl.-x-us-high-y-corp-bond",
		"https://jp.investing.com/etfs/managed-futures-strategy-fund",
		"https://jp.investing.com/etfs/wisdomtree-em-local-debt",
		"https://jp.investing.com/etfs/unitedstates-12-m.-natural-gas-fu.",
		"https://jp.investing.com/etfs/guggenheim-multi-asset-income",
		"https://jp.investing.com/etfs/united-states-gasoline-fund-lp",
		"https://jp.investing.com/etfs/marketvectors-long-municipal-index",
		"https://jp.investing.com/etfs/guggenheim-china-smlcap",
		"https://jp.investing.com/etfs/claymore-china-real-estate",
		"https://jp.investing.com/etfs/spdr-barclays-1-10-year-tips",
		"https://jp.investing.com/etfs/proshares-ultrapro-short-fin",
		"https://jp.investing.com/etfs/etfs-physical-platinum-shares",
		"https://jp.investing.com/etfs/proshares-short-7-10-year-treasury",
		"https://jp.investing.com/etfs/rydex-s-p-equal-weight-health-care",
		"https://jp.investing.com/etfs/revenueshares-mid-cap",
		"https://jp.investing.com/etfs/direxion-nq-100-equal-weighted",
		"https://jp.investing.com/etfs/revenueshares-small-cap",
		"https://jp.investing.com/etfs/proshares-ultra-semiconductors",
		"https://jp.investing.com/etfs/spdr-s-p-transportation",
		"https://jp.investing.com/etfs/proshares-hedge-replication",
		"https://jp.investing.com/etfs/ipath-global-carbon",
		"https://jp.investing.com/etfs/egshares-india-small-cap",
		"https://jp.investing.com/etfs/ishares-s-p-global-materials",
		"https://jp.investing.com/etfs/ishares-djsu-oil-equipment---serv.",
		"https://jp.investing.com/etfs/ishares-s-p---global-100",
		"https://jp.investing.com/etfs/proshares-ultra-midcap400",
		"https://jp.investing.com/etfs/market-vectors-intl-hyield-bond",
		"https://jp.investing.com/etfs/wisdomtree-dividend-x-financials",
		"https://jp.investing.com/etfs/ishares-core-long-term-u.s.-bond",
		"https://jp.investing.com/etfs/spdr-s-p-600-small-cap",
		"https://jp.investing.com/etfs/marketvectors-short-municipal",
		"https://jp.investing.com/etfs/vanguard-s-p-mid-cap-400-growth",
		"https://jp.investing.com/etfs/pshares-ftse-rafi-dm-x-us-sml-mid",
		"https://jp.investing.com/etfs/proshares-ultrashort-silver",
		"https://jp.investing.com/etfs/guggenheim-defensive-equity",
		"https://jp.investing.com/etfs/spdr-s-p-health-care-equipment",
		"https://jp.investing.com/etfs/pimco-15-year-us-tips-index-fund",
		"https://jp.investing.com/etfs/spdr-ftse-macquarie-gi-100",
		"https://jp.investing.com/etfs/ishares-s-p-global-telecom.",
		"https://jp.investing.com/etfs/powershares-dynamic-oil-services",
		"https://jp.investing.com/etfs/direxion-daily-retail-bull-2x",
		"https://jp.investing.com/etfs/proshares-ultrash.-lehman-7-10-y",
		"https://jp.investing.com/etfs/powershares-db-agriculture-2x-long",
		"https://jp.investing.com/etfs/united-states-12-month-oil",
		"https://jp.investing.com/etfs/firsttrust-s-p-reit-index-fund",
		"https://jp.investing.com/etfs/wisdomtree-total-dividend-fund",
		"https://jp.investing.com/etfs/direxion-daily-natural-gas-bear-2x",
		"https://jp.investing.com/etfs/db-x-msci-em-currency-hedged-eq",
		"https://jp.investing.com/etfs/wisdomtree-asia-pacific-x-japan",
		"https://jp.investing.com/etfs/vanguard-s-p-mid-cap-400-value",
		"https://jp.investing.com/etfs/wisdomtree-dreyfus-chinese-yuan",
		"https://jp.investing.com/etfs/short-ftse-xinhua-china",
		"https://jp.investing.com/etfs/physical-pr.-metals-basket-sh.",
		"https://jp.investing.com/etfs/proshares-ultrashort-gold",
		"https://jp.investing.com/etfs/powershares-s-p500-down-hdg",
		"https://jp.investing.com/etfs/proshares-ultra-xinhua-china-25",
		"https://jp.investing.com/etfs/market-vectors-retail",
		"https://jp.investing.com/etfs/spdr-bofa-crossover-corp-bond",
		"https://jp.investing.com/etfs/vanguard-s-p-small-cap-600-growth",
		"https://jp.investing.com/etfs/marketvectors-africa-index",
		"https://jp.investing.com/etfs/powershares-dynamic-media",
		"https://jp.investing.com/etfs/spdr-mortgage-backed-bond",
		"https://jp.investing.com/etfs/short-real-estate",
		"https://jp.investing.com/etfs/powershares-db-crude-oil-short",
		"https://jp.investing.com/etfs/ishares-global-high-y-corp-bond",
		"https://jp.investing.com/etfs/ishares-morningstar-small-value",
		"https://jp.investing.com/etfs/guggenheim-spin-off",
		"https://jp.investing.com/etfs/cambria-shareholder-yield",
		"https://jp.investing.com/etfs/proshares-ultra-basic-materials",
		"https://jp.investing.com/etfs/powershares-dynamic-energy-e-p",
		"https://jp.investing.com/etfs/ipath-dj-ubs-agric.-subindex-tr",
		"https://jp.investing.com/etfs/alps-alerian-energy-infra",
		"https://jp.investing.com/etfs/wisdomtree-dreyfus-brazilian-real",
		"https://jp.investing.com/etfs/proshares-ultrashort-msci-eafe",
		"https://jp.investing.com/etfs/ishares-russell-top-200",
		"https://jp.investing.com/etfs/wisdomtree-total-earnings",
		"https://jp.investing.com/etfs/ishares-2018-amtfree-muni-term",
		"https://jp.investing.com/etfs/powersh.-dynamic-biotech---genome",
		"https://jp.investing.com/etfs/ishares-s-p-global-cons.discr.",
		"https://jp.investing.com/etfs/global-x-ftse-nordic-30",
		"https://jp.investing.com/etfs/guggenheim-raymond-james-sb-1-eq",
		"https://jp.investing.com/etfs/guggenheim-global-timber",
		"https://jp.investing.com/etfs/peritus-high-yield-etf",
		"https://jp.investing.com/etfs/ishares-ftse-nareit-residential",
		"https://jp.investing.com/etfs/rydex-s-p-equal-weight-industrials",
		"https://jp.investing.com/etfs/ishares-djsu-health-care-providers",
		"https://jp.investing.com/etfs/ishares-s-p-topix-150",
		"https://jp.investing.com/etfs/marketvectors-mortgage-reit-income",
		"https://jp.investing.com/etfs/spdr-multi-asset-real-return",
		"https://jp.investing.com/etfs/rydex-s-p-equal-weight-materials",
		"https://jp.investing.com/etfs/proshares-ultra-msci-emerging-mrkt",
		"https://jp.investing.com/etfs/ishares-morningstar-mid-core-index",
		"https://jp.investing.com/etfs/global-x-top-guru-holdings",
		"https://jp.investing.com/etfs/spdr-ssga-ul",
		"https://jp.investing.com/etfs/ishares-msci-belgium",
		"https://jp.investing.com/etfs/proshares-ultrash.-djubs-ntrl-gas",
		"https://jp.investing.com/etfs/proshares-ultra-euro",
		"https://jp.investing.com/etfs/msci-ireland-capped-invest.-mrkt",
		"https://jp.investing.com/etfs/global-x-nigeria-index",
		"https://jp.investing.com/etfs/firsttrust-ise-global-wind-energy",
		"https://jp.investing.com/etfs/renaissance-ipo",
		"https://jp.investing.com/etfs/ipath-dj-aig-nickel",
		"https://jp.investing.com/etfs/rydex-s-p-midcap-400-pure-value",
		"https://jp.investing.com/etfs/advisorshares-newfleet-mult-sect",
		"https://jp.investing.com/etfs/ishares-barclays-cmbs-bond-fund",
		"https://jp.investing.com/etfs/spdr-s-p-health-care-services",
		"https://jp.investing.com/etfs/rogers-intl-commodity-energy",
		"https://jp.investing.com/etfs/proshares-ultrashort-msci-japan",
		"https://jp.investing.com/etfs/ishares-aaa---a-rated-corp-bond",
		"https://jp.investing.com/etfs/marketvectors-china",
		"https://jp.investing.com/etfs/global-x-ftse-asean-40",
		"https://jp.investing.com/etfs/wisdomtree-intl-midcap-dividend",
		"https://jp.investing.com/etfs/barclays-etn--shiller-cape-etn",
		"https://jp.investing.com/etfs/proshares-ultrashort-industrials",
		"https://jp.investing.com/etfs/ishares-msci-global-energy-prod.",
		"https://jp.investing.com/etfs/guggenheim-mid-cap-core",
		"https://jp.investing.com/etfs/rydex-currencyshares-aud-trust",
		"https://jp.investing.com/etfs/cambria-foreign-shareholdr-yld",
		"https://jp.investing.com/etfs/ishares-goldman-sachs-network",
		"https://jp.investing.com/etfs/morningstar-us-market-factor-tilt",
		"https://jp.investing.com/etfs/wisdomtree-intl-real-estate-fund",
		"https://jp.investing.com/etfs/guggenheim-s-p-global-div.-opp.",
		"https://jp.investing.com/etfs/powershares-dynamic-leisure---ent.",
		"https://jp.investing.com/etfs/spdr-kbw-capital-markets",
		"https://jp.investing.com/etfs/ishares-ibds-mar-2020-corp-trm",
		"https://jp.investing.com/etfs/ubs-etracs-bloomberg-cmci",
		"https://jp.investing.com/etfs/ishares-djsu-insurance",
		"https://jp.investing.com/etfs/marketvectors-unconv.-oil---gas",
		"https://jp.investing.com/etfs/powershares-dynamic-software",
		"https://jp.investing.com/etfs/ishares-morningstar-large-value",
		"https://jp.investing.com/etfs/wisdomtree-intl-dividend-top-100",
		"https://jp.investing.com/etfs/powershares-vrdo-tax-free-weekly",
		"https://jp.investing.com/etfs/ishares-s-p-global-con.-stap.",
		"https://jp.investing.com/etfs/guggenheim-canada-energy-income",
		"https://jp.investing.com/etfs/ishares-barclays-agency-bond",
		"https://jp.investing.com/etfs/spdr-s-p-global-dividend",
		"https://jp.investing.com/etfs/proshares-ultra-health-care",
		"https://jp.investing.com/etfs/powershares-db-gold-fund",
		"https://jp.investing.com/etfs/marketvectors-gaming",
		"https://jp.investing.com/etfs/arrow-dow-jones-global-yield",
		"https://jp.investing.com/etfs/proshares-ultrashort-midcap400",
		"https://jp.investing.com/etfs/powershares---global-clean-energy",
		"https://jp.investing.com/etfs/ultra-msci-brazil",
		"https://jp.investing.com/etfs/spdr-russell-2000-low-vol",
		"https://jp.investing.com/etfs/ishares-djsu-pharmaceutical-index",
		"https://jp.investing.com/etfs/powershares-db-precious-metals",
		"https://jp.investing.com/etfs/dj-high-yield-select-10-etn",
		"https://jp.investing.com/etfs/global-x-fertilizers-potash",
		"https://jp.investing.com/etfs/direxion-latin-america-3x-bull",
		"https://jp.investing.com/etfs/ishares-msci-israel-cap-inv.-mrkt",
		"https://jp.investing.com/etfs/powershares-cleantech-portfolio",
		"https://jp.investing.com/etfs/vanguard-s-p-small-cap-600-value",
		"https://jp.investing.com/etfs/direxion-developed-markets-bull-3x",
		"https://jp.investing.com/etfs/direxion-developed-markets-bear-3x",
		"https://jp.investing.com/etfs/spdr-s-p-telecom",
		"https://jp.investing.com/etfs/powersharesamental-pure-mid-value",
		"https://jp.investing.com/etfs/spdr-income-allocation",
		"https://jp.investing.com/etfs/proshares-global-listed-prvt",
		"https://jp.investing.com/etfs/rydex-s-p-smallcap-600-pure-growth",
		"https://jp.investing.com/etfs/alps-coh.-ste.-global-realty-maj.",
		"https://jp.investing.com/etfs/ishares-s-p-developed-x-us-prop.",
		"https://jp.investing.com/etfs/spdr-s-p-software---services",
		"https://jp.investing.com/etfs/ipath-pure-beta-cocoa",
		"https://jp.investing.com/etfs/powershares-insured-ny-mun.-bond",
		"https://jp.investing.com/etfs/yorkville-high-income-mlp",
		"https://jp.investing.com/etfs/powersh.-rafi-asia-pacific-x-japan",
		"https://jp.investing.com/etfs/guggenheim-birc",
		"https://jp.investing.com/etfs/db-x-trackers-muni-infras-revn",
		"https://jp.investing.com/etfs/ultra-msci-europe",
		"https://jp.investing.com/etfs/proshares-ultra-7-10-year-treasury",
		"https://jp.investing.com/etfs/firsttrust-dj-select-microcap",
		"https://jp.investing.com/etfs/ishares-ibds-mar-2018-corp-trm",
		"https://jp.investing.com/etfs/wisdomtree-europe-high-yielding-eq",
		"https://jp.investing.com/etfs/firsttrust-epra-nareit-global-re",
		"https://jp.investing.com/etfs/marketvectors-brazil-small-cap",
		"https://jp.investing.com/etfs/rydex-s-p-midcap-400-pure-growth",
		"https://jp.investing.com/etfs/etracs-mon.-pay-2xlev.-dj-s.-div.",
		"https://jp.investing.com/etfs/etfs-physical-palladium-shares",
		"https://jp.investing.com/etfs/proshares-ultra-yen",
		"https://jp.investing.com/etfs/ishares-msci-norway-cap-inv.-mrkt",
		"https://jp.investing.com/etfs/firsttrust-value-line-100-fund",
		"https://jp.investing.com/etfs/proshares-ultra-msci-eafe",
		"https://jp.investing.com/etfs/ultrapro-midcap400",
		"https://jp.investing.com/etfs/morgan-st.-cushing-mlp-high-income",
		"https://jp.investing.com/etfs/spdr-dj-global-titans",
		"https://jp.investing.com/etfs/alps-equal-sector-weight",
		"https://jp.investing.com/etfs/ishares-msci-germany-small-cap",
		"https://jp.investing.com/etfs/ultrapro-short-midcap400",
		"https://jp.investing.com/etfs/powershares-dynamic-dev-int-opp",
		"https://jp.investing.com/etfs/ipath-gsci-tr-index",
		"https://jp.investing.com/etfs/powersharesamental-pure-large-core",
		"https://jp.investing.com/etfs/powershares-xtf:-dynamic-market",
		"https://jp.investing.com/etfs/short-term-municipal-bond-strategy",
		"https://jp.investing.com/etfs/teucrium-agricultural-fund",
		"https://jp.investing.com/etfs/ishares-msci-china-small-cap",
		"https://jp.investing.com/etfs/rydex-s-p-equal-weight-utilities",
		"https://jp.investing.com/etfs/ishares-msci-denmark-cap-inv.-mrkt",
		"https://jp.investing.com/etfs/prosh.ultrashort-consumer-goods",
		"https://jp.investing.com/etfs/guggenheim-insider",
		"https://jp.investing.com/etfs/direxion-10-yr-tr.-bear-3x-shrs",
		"https://jp.investing.com/etfs/powershares-db-g10-curr.-harvest",
		"https://jp.investing.com/etfs/marketvectors-hard-assets-prod.",
		"https://jp.investing.com/etfs/powersharesamental-pure-small",
		"https://jp.investing.com/etfs/quantshares-us-mkt-neut-anti-beta",
		"https://jp.investing.com/etfs/united-states-short-oil-fund",
		"https://jp.investing.com/etfs/ipath-gems-asia-8",
		"https://jp.investing.com/etfs/powershares-db-gold-short",
		"https://jp.investing.com/etfs/db-x-trackers-msci-brazil-hgd-eq",
		"https://jp.investing.com/etfs/revenueshares-financials-sector",
		"https://jp.investing.com/etfs/marketvectors-pre-refunded-mun.",
		"https://jp.investing.com/etfs/ishares-ibds-mar-2023-corp-exfincl",
		"https://jp.investing.com/etfs/united-states-copper-index-fund",
		"https://jp.investing.com/etfs/wisdomtree-world-ex-su-growth-fund",
		"https://jp.investing.com/etfs/etracs-dj-ubs-commodity-index-tr",
		"https://jp.investing.com/etfs/ready-access-variable-income-fund",
		"https://jp.investing.com/etfs/spdr-msci-acwi-imi",
		"https://jp.investing.com/etfs/flexshares-quality-div-dynamic",
		"https://jp.investing.com/etfs/yorkville-h",
		"https://jp.investing.com/etfs/msci-global-agri.-producers-fund",
		"https://jp.investing.com/etfs/elements-mlcx-grains-index-tr",
		"https://jp.investing.com/etfs/proshares-ultrashort-smallcap600",
		"https://jp.investing.com/etfs/powers.-wilderhill-prog.-energy",
		"https://jp.investing.com/etfs/barclays-etn-fi-enhanced-europe-50",
		"https://jp.investing.com/etfs/marketvectors-global-alt.-energy",
		"https://jp.investing.com/etfs/ishares-msci-finland-cap-inv.-mrkt",
		"https://jp.investing.com/etfs/proshares-ultrashort-utilities",
		"https://jp.investing.com/etfs/proshares-ultra-industrials",
		"https://jp.investing.com/etfs/ipath-dj-ubs-cotton-tr-sub-index",
		"https://jp.investing.com/etfs/global-x-china-materials",
		"https://jp.investing.com/etfs/marketvectors-poland",
		"https://jp.investing.com/etfs/ishares-ibds-mar-2020-corp-exfincl",
		"https://jp.investing.com/etfs/ishares-morningstar-mid-growth",
		"https://jp.investing.com/etfs/ishares-msci-usa-size-factor",
		"https://jp.investing.com/etfs/proshares-ultrashort-health-care",
		"https://jp.investing.com/etfs/proshares-ultra-utilities",
		"https://jp.investing.com/etfs/ishares-morningstar-small-core",
		"https://jp.investing.com/etfs/market-vectors-israel",
		"https://jp.investing.com/etfs/iq-global-agribusiness-small-cap",
		"https://jp.investing.com/etfs/beyond-bircs",
		"https://jp.investing.com/etfs/advisorshares-trimtabs-flt-shrink",
		"https://jp.investing.com/etfs/rydex-s-p-equal-weight-cons.-dis.",
		"https://jp.investing.com/etfs/firsttrust-ise-glb-engnrg---const",
		"https://jp.investing.com/etfs/wisdomtree-australia-dividend-fund",
		"https://jp.investing.com/etfs/guggenheim-intl-mul.-asset-income",
		"https://jp.investing.com/etfs/iq-cpi-inflation-hedged",
		"https://jp.investing.com/etfs/rydex-s-p-smallcap-600-pure-value",
		"https://jp.investing.com/etfs/market-vectors-2x-short-euro-etn",
		"https://jp.investing.com/etfs/ipath-pure-beta-broad-commodity",
		"https://jp.investing.com/etfs/ishares-msci---kokusai",
		"https://jp.investing.com/etfs/spdr-issuer-scored-corp-bond",
		"https://jp.investing.com/etfs/franklin-short-duration-us-gov",
		"https://jp.investing.com/etfs/powershares-dynamic-retail",
		"https://jp.investing.com/etfs/ubs-etracs-long-platinum-tr",
		"https://jp.investing.com/etfs/ipath-pure-beta-agriculture",
		"https://jp.investing.com/etfs/iq-arb-global-resources-etf",
		"https://jp.investing.com/etfs/ipath-msci-india-index-etn",
		"https://jp.investing.com/etfs/wisdomtree-dreyfus-emerging-curr.",
		"https://jp.investing.com/etfs/wisdomtree-low-p-e-fund",
		"https://jp.investing.com/etfs/alphaclone-alternative-alpha",
		"https://jp.investing.com/etfs/ishares-asia-pacific-dividend-30",
		"https://jp.investing.com/etfs/gs-s-p-gsci-enhanced-commodity-tr",
		"https://jp.investing.com/etfs/spdr-s-p-1500-value-tilt",
		"https://jp.investing.com/etfs/global-x-next-emer---frontier",
		"https://jp.investing.com/etfs/market-vectors-indian-rupee-usd",
		"https://jp.investing.com/etfs/pimco-broad-us-tips-index-fund",
		"https://jp.investing.com/etfs/first-trust-morningstar-futs-strat",
		"https://jp.investing.com/etfs/etracs-monthly-pay-2x-lev.-s-p-div",
		"https://jp.investing.com/etfs/powershares-db-crude-oil-long",
		"https://jp.investing.com/etfs/spdr-russell-1000-low-vol",
		"https://jp.investing.com/etfs/proshares-ultra-msci-japan",
		"https://jp.investing.com/etfs/powershares-db-base-metals-2x-long",
		"https://jp.investing.com/etfs/powershares-global-em-infr.",
		"https://jp.investing.com/etfs/s-p-500-dynamic-vix-etn",
		"https://jp.investing.com/etfs/ishares-morningstar-small-growth",
		"https://jp.investing.com/etfs/spdr-s-p-1500-momentum-tilt",
		"https://jp.investing.com/etfs/guggenheim-china-all-cap",
		"https://jp.investing.com/etfs/ipath-pure-beta-crude-oil",
		"https://jp.investing.com/etfs/proshares-ultra-consumer-services",
		"https://jp.investing.com/etfs/wisdomtree-asia-local-debt-fund",
		"https://jp.investing.com/etfs/flexshares-int-qual-div-dyn",
		"https://jp.investing.com/etfs/proshares-short-smallcap600",
		"https://jp.investing.com/etfs/rydex-currencyshares-swedish-krona",
		"https://jp.investing.com/etfs/rydex-russell-2000-equal-weight",
		"https://jp.investing.com/etfs/ipath-dj-ubs-tin-tr-sub-index",
		"https://jp.investing.com/etfs/huntington-ecological-strategy",
		"https://jp.investing.com/etfs/powersharesamental-pure-mid-core",
		"https://jp.investing.com/etfs/powershares-db-silver-fund",
		"https://jp.investing.com/etfs/morningstar-wide-moat-focus-etn",
		"https://jp.investing.com/etfs/ishares-lehman-gov.-credit-bond",
		"https://jp.investing.com/etfs/barclays-etn-s-p-veqtor-etn",
		"https://jp.investing.com/etfs/iq-hedge-market-neutral-tracker",
		"https://jp.investing.com/etfs/marketvectors-russia-small-cap",
		"https://jp.investing.com/etfs/powersharesamental-pure-small-core",
		"https://jp.investing.com/etfs/proshares-rafi-long-short",
		"https://jp.investing.com/etfs/proshares-ultra-telecom.-proshares",
		"https://jp.investing.com/etfs/marketvectors-latam-aggregate-bond",
		"https://jp.investing.com/etfs/powershares-db-agriculture-x2-short",
		"https://jp.investing.com/etfs/db-x-trackers-msci-ap-x-jpn-hgd-eq",
		"https://jp.investing.com/etfs/rydex-msci-em-eq-weight",
		"https://jp.investing.com/etfs/iq-hedge-macro-tracker",
		"https://jp.investing.com/etfs/global-x-china-energy",
		"https://jp.investing.com/etfs/quantshares-us-market-neutral",
		"https://jp.investing.com/etfs/ipath-dj-ubs-softs-tr-sub-index",
		"https://jp.investing.com/etfs/etracs-1xmon.-sh.-al.-mlp-infr.-tr",
		"https://jp.investing.com/etfs/advisorshares-madrona-global-bond",
		"https://jp.investing.com/etfs/powershares-zacks-micro-cap",
		"https://jp.investing.com/etfs/meidell-tactical-advantage",
		"https://jp.investing.com/etfs/wilshire-micro-cap",
		"https://jp.investing.com/etfs/marketvectors-nuclear-energy",
		"https://jp.investing.com/etfs/market-vectors-env-svcs",
		"https://jp.investing.com/etfs/claymore-cef-gs-connect-etn",
		"https://jp.investing.com/etfs/kraneshares-csi-china-5-y-plan",
		"https://jp.investing.com/etfs/proshares-ultra-consumer-goods",
		"https://jp.investing.com/etfs/etracs-alerian-natural-gas-mlp",
		"https://jp.investing.com/etfs/rogers-intl-commodity-metal",
		"https://jp.investing.com/etfs/short-basic-materials",
		"https://jp.investing.com/etfs/advisorshares-madrona-intl",
		"https://jp.investing.com/etfs/ishares-msci-u.k.-small-cap",
		"https://jp.investing.com/etfs/market-vectors-renminbi-usd",
		"https://jp.investing.com/etfs/ipath-dj-ubs-energy-tr-sub-index",
		"https://jp.investing.com/etfs/ubs-etracs-cmci-livestock-tr",
		"https://jp.investing.com/etfs/ipath-dj-ubs-pr.-metals-tr-subin.",
		"https://jp.investing.com/etfs/proshares-merger",
		"https://jp.investing.com/etfs/advisorshares-madrona-domestic",
		"https://jp.investing.com/etfs/proshares-short-oil---gas",
		"https://jp.investing.com/etfs/powershares-db-agriculture-long",
		"https://jp.investing.com/etfs/velocityshares-tail-risk-hgd-lg-cp",
		"https://jp.investing.com/etfs/ultrashort-australian-dollar",
		"https://jp.investing.com/etfs/iq-global-oil-small-cap",
		"https://jp.investing.com/etfs/powershares-db-base-metals-2x-sh.",
		"https://jp.investing.com/etfs/velocityshares-vol-hdgd-lg-cp",
		"https://jp.investing.com/etfs/renaissance-international-ipo-etf",
		"https://jp.investing.com/etfs/powershares-db-base-metals-short",
		"https://jp.investing.com/etfs/deutsche-bank-commodity-x2-short",
		"https://jp.investing.com/etfs/star-global-buy-write",
		"https://jp.investing.com/etfs/ipath-dj-ubs-aluminum-tr-sub-index",
		"https://jp.investing.com/etfs/powershares-crude-oil-2x-short-us",
		"https://jp.investing.com/etfs/proshares-ultrashort-consumer-ser.",
		"https://jp.investing.com/etfs/firsttrust-australia-alphadex-fund",
		"https://jp.investing.com/etfs/iq-australia-small-cap",
		"https://jp.investing.com/etfs/ubs-etracs-bloomberg-cmci-food",
		"https://jp.investing.com/etfs/advisorshares-pacific-asset-enhance",
		"https://jp.investing.com/etfs/united-states-heating-oil-fund-lp",
		"https://jp.investing.com/etfs/proshares-short-euro",
		"https://jp.investing.com/etfs/egshares-low-volatility-em-div.",
		"https://jp.investing.com/etfs/direxion-daily-bond-mtkt-bear-1x",
		"https://jp.investing.com/etfs/ishares-ibds-mar-2018-corp-exfincl",
		"https://jp.investing.com/etfs/direxion-10-yr-tr.-bull-3x-shrs",
		"https://jp.investing.com/etfs/daily-20-year-plus-tr.-bear-1x",
		"https://jp.investing.com/etfs/ipath-pure-beta-sugar",
		"https://jp.investing.com/etfs/proshares-ultra-smallcap600",
		"https://jp.investing.com/etfs/quantshares-us-market-neutral-mom.",
		"https://jp.investing.com/etfs/powershares-s-p-intl-dev-high-beta",
		"https://jp.investing.com/etfs/direxion-daily-7-10-yr-trsry-br-1x",
		"https://jp.investing.com/etfs/ipath-inv.-s-p500-vix-shterm-fut.",
		"https://jp.investing.com/etfs/spectrum-lg-cap-us-sector-etn",
		"https://jp.investing.com/etfs/ubs-etracs-cmci-silver-tr",
		"https://jp.investing.com/etfs/wilshire-us-reit",
		"https://jp.investing.com/etfs/ipath-gems-index",
		"https://jp.investing.com/etfs/ipath-optimized-currency-carry",
		"https://jp.investing.com/etfs/currencyshares-chinese-renminbi-tr",
		"https://jp.investing.com/etfs/global-x-china-industrials",
		"https://jp.investing.com/etfs/quantshares-us-mrkt-neut-size",
		"https://jp.investing.com/etfs/powershares-db-commodity-2x-long",
		"https://jp.investing.com/etfs/powershares-db-commodity-short",
		"https://jp.investing.com/etfs/powershares-active-us-real-estate",
		"https://jp.investing.com/etfs/ipath-dj-ubs-platinum-tr-sub-index",
		"https://jp.investing.com/etfs/ipath-seasonal-natural-gas",
		"https://jp.investing.com/etfs/ubs-etracs-cmci-gold-tr",
		"https://jp.investing.com/etfs/iq-canada-small-cap",
		"https://jp.investing.com/indices/japan-ni225",
		"https://jp.investing.com/indices/japan-225-futures",
		"https://jp.investing.com/indices/us-30",
		"https://jp.investing.com/indices/germany-30",
		"https://jp.investing.com/indices/aus-200",
		"https://jp.investing.com/indices/uk-100",
		"https://jp.investing.com/quotes/us-dollar-index",
		"https://jp.investing.com/currencies/bitcoin-futures",
		"https://jp.investing.com/commodities/gold",
		"https://jp.investing.com/commodities/crude-oil",
		"https://jp.investing.com/commodities/silver",
		"https://jp.investing.com/commodities/us-cotton-no.2",
		"https://jp.investing.com/commodities/carbon-emissions",
		"https://jp.investing.com/commodities/us-corn",
		"https://jp.investing.com/commodities/us-coffee-c",
		"https://jp.investing.com/commodities/aluminum",
		"https://jp.investing.com/currencies/usd-jpy",
		"https://jp.investing.com/currencies/eur-usd",
		"https://jp.investing.com/currencies/eur-jpy",
		"https://jp.investing.com/currencies/try-jpy",
		"https://jp.investing.com/currencies/aud-jpy",
		"https://jp.investing.com/currencies/gbp-jpy",
		"https://jp.investing.com/currencies/gbp-usd",
		"https://jp.investing.com/currencies/jpy-try",
		"https://jp.investing.com/crypto/bitcoin/btc-usd",
		"https://jp.investing.com/crypto/bitcoin/btc-jpy",
		"https://jp.investing.com/crypto/bitcoin-cash/bch-usd",
		"https://jp.investing.com/crypto/ethereum/eth-jpy",
		"https://jp.investing.com/crypto/ethereum/eth-usd",
		"https://jp.investing.com/crypto/ripple/xrp-btc",
		"https://jp.investing.com/crypto/ripple/xrp-usd",
		"https://jp.investing.com/crypto/monaco/mco-btc",
		"https://jp.investing.com/currencies/usd-jpy",
		"https://jp.investing.com/currencies/eur-jpy",
		"https://jp.investing.com/currencies/aud-jpy",
		"https://jp.investing.com/currencies/brl-jpy",
		"https://jp.investing.com/currencies/gbp-jpy",
		"https://jp.investing.com/currencies/usd-krw",
		"https://jp.investing.com/currencies/eur-usd",
		"https://jp.investing.com/equities/pacific-net-co-ltd",
		"https://jp.investing.com/equities/knc-laboratories-co-ltd",
		"https://jp.investing.com/equities/jtec-corp",
		"https://jp.investing.com/equities/aval-data-corp",
		"https://jp.investing.com/equities/marushohotta-co-ltd",
		"https://jp.investing.com/equities/ina-research-inc",
		"https://jp.investing.com/equities/ishii-hyoki-co-ltd",
		"https://jp.investing.com/equities/carchs-holdings-co-ltd"
		]
	for target_url in target_lst:
		get_historical_items(target_url)



def main():
	url = "https://jp.investing.com/"
	login(url)
	for page in get_list_pages(url)[int(args[1]):int(args[2])]:
		for item in get_whole_items(page['url']):
			while True:
				try:
					target_url = item['url']
					print(target_url)
					get_historical_items(target_url)
					break

				except Exception as e:
					err_r = [target_url, e]
					save_contents_into_file(err_r, ERR_URL_PATH)
					driver.refresh()
					if str(e).find("Cannot navigate to invalid URL"):
						break					
					# driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chromeOptions)
					pass

			# save_file_as_csv(target_id, get_historical_items(target_url))
			# save_id_into_list(target_id)



def save_contents_into_file(content, f_path):
	f = open(f_path, 'a')
	f.write(str(content) + "\n")
	f.close()

def is_downloaded(target_id):
	downloaded_id_list = []
	with open(DOWNLOADED_URL_PATH, 'r') as f:
		for line in f:
			downloaded_id_list.append(line.replace("\n", ""))
	# print(downloaded_id_list)
	if target_id in downloaded_id_list:
		return True
	else:
		return False

# def is_saved(json, name):
# 	csv = change_to_CSV(json)
# 	with open(os.path.join(cwd, 'sources_invest/' + name + '.csv')) as f:
# 		contents = f.read()
# 	if contents.find(csv):
# 		return True
# 	else:
# 		return False


# def change_to_CSV(json_contents):
# 	csv_contents = []
# 	for json in json_contents:
# 		csv_r = (str(json['invest_id']) + ',' +
# 						str(json['date']) + ',' + 
# 						str(json['start_price']) + ',' + 
# 						str(json['high_price']) + ',' + 
# 						str(json['low_price']) + ',' + 
# 						str(json['end_price']) + ',' + 
# 						str(json['name']))
# 		csv_contents.append(csv_r)
# 	return csv_contents


# def save_file_as_csv(name, contents):
# 	csv_contents = change_to_CSV(contents)
# 	with open(os.path.join(cwd, 'sources_invest/' + name + '.csv'), 'a') as f: 
# 		for csv_content in csv_contents:
# 			f.write(str(csv_content) + "\n")
		

@timeout_decorator.timeout(120)
def get_historical_items(base_url):
	start = time.time()

	driver.get(base_url)
	url_list = []
	a_lst = driver.find_elements_by_css_selector("ul.arial_12 > li > a")
	invest_id = driver.find_element_by_css_selector("h1.float_lang_base_1").text
	historical_url = ""
	for a in a_lst:
		if a.get_attribute("href").find("historical") > 0:
			historical_url = a.get_attribute("href")
			break
	isNotOpened = True # Not to open url before check "is_downloaded"

	# for cur_oldest_date in [["1980/01/01", "1997/12/31"], ["1998/01/01", "2015/12/31"], ["2016/01/01", "2019/01/01"]]:
	for cur_oldest_date in [["2018/04/01", "2018/06/30"]]:
		if is_downloaded(str([historical_url, cur_oldest_date])):
			print("--- " + str([historical_url, cur_oldest_date]) + " DOWNLOADED ---")
			continue
		else:
			if isNotOpened:
				driver.get(historical_url)
				isNotOpened = False

		print("***** " + str([historical_url, cur_oldest_date]) + " DOWNLOADING")
		while True:
			calender_btn = driver.find_element_by_css_selector("div.float_lang_base_1#widget")
			try:
				calender_btn.click()
				driver.implicitly_wait(10)
				start_date_input = driver.find_element_by_css_selector("input.newInput#startDate")
				start_date_input.clear()
				start_date_input.send_keys(cur_oldest_date[0])
				end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
				end_date_input.clear()
				end_date_input.send_keys(cur_oldest_date[1])
				break

			except Exception as e:
				driver.save_screenshot('search_results.png') 
				pass

		while True:
			try:
				end_date_input.send_keys(Keys.RETURN)
				driver.implicitly_wait(30)
				# WebDriverWait(driver, 10).until(
				# 	EC.title_contains("Google")
				# )

				# dwnld_btn = driver.find_element_by_css_selector("a.newBtn.LightGray.downloadBlueIcon.js-download-hist-data")
				dwnld_btn = driver.find_element_by_css_selector("a.newBtn.LightGray.downloadBlueIcon.js-download-data")
				dwnld_btn.click()
				break
			except:
				end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
				pass


		# while True:
		# 	try:
		# 		end_date_input.send_keys(Keys.RETURN)
		# 		driver.implicitly_wait(10)
		# 		historical_item_lst = driver.find_elements_by_css_selector("div#results_box > table#curr_table > tbody > tr")
		# 		print("enter clicked")
		# 		break
		# 	except:
		# 		driver.save_screenshot('search_results.png') 
		# 		end_date_input = driver.find_element_by_css_selector("input.newInput#endDate")
		# 		pass
		# for historical_item in historical_item_lst:
		# 	try:
		# 		historical_item_val = historical_item.find_elements_by_css_selector("td")
		# 		url = {
		# 				# 'date': historical_item_val[0].text,
		# 				# 'invest_id': base_url.split("/")[-1],
		# 				# 'name': invest_id,
		# 				# 'end_price': historical_item_val[1].text,
		# 				# 'start_price': historical_item_val[2].text,
		# 				# 'high_price': historical_item_val[3].text,
		# 				# 'low_price': historical_item_val[4].text,
		# 				'date': historical_item_val[0].text,
		# 				'invest_id': base_url.split("/")[-1],
		# 				'name': invest_id,
		# 				'end_price': historical_item_val[1].get_attribute("data-real-value"),
		# 				'start_price': historical_item_val[2].get_attribute("data-real-value"),
		# 				'high_price': historical_item_val[3].get_attribute("data-real-value"),
		# 				'low_price': historical_item_val[4].get_attribute("data-real-value"),
		# 				# 'output': historical_item_val[5].text,
		# 				# 'preb_change': historical_item_val[6].text,
		# 			}
		# 		# if is_saved([url], invest_id):
		# 		# 	continue  # On the assumption that the items is in order of its date
		# 		url_list.append(url)
		# 		# print(str(len(url_list)) + "/" + str(len(historical_item_lst)) + " has done...")
		# 	except Exception as e:
		# 		print(e)
		# 		pass
		# print("hist_lst: " + str(len(historical_item_lst)))
		save_contents_into_file(str([historical_url, cur_oldest_date]), DOWNLOADED_URL_PATH)
		elapsed_time = time.time() - start
		print ("Download_time:{0}".format(elapsed_time) + "[sec] *****")
	return url_list	


def get_whole_items(base_url):
	start = time.time()
	driver.get(base_url)
	url_list = []
	for a in driver.find_elements_by_css_selector("tbody > tr > td > a"):
		if a.get_attribute('href') == "javascript:void(0);":
			continue
		url = {
				'key': a.text,
				'url': a.get_attribute('href'),
			}
		url_list.append(url)
	elapsed_time = time.time() - start
	print ("*** [get_whole_items]elapsed_time:{0}".format(elapsed_time) + "[sec]")
	return url_list	


def get_list_pages(base_url):
	start = time.time()
	driver.get(base_url)
	url_list = []
	for a in driver.find_elements_by_css_selector("ul.subMenuNav > li > div > ul > li > a"):
		url = {
				'key': a.text,
				'url': a.get_attribute('href'),
			}
		url_list.append(url)
		# break # For test
	elapsed_time = time.time() - start
	print ("*** [get_list_pages]elapsed_time:{0}".format(elapsed_time) + "[sec]")
	return url_list


def login(base_url):
	mail_str = "masa.ochi.74@gmail.com"
	pswd_str = "12761masa"
	driver.get(base_url)
	while True:
		try:
			login_btn = driver.find_element_by_css_selector("div.topBarText > a.login.bold")
			login_btn.click()
			login_form = driver.find_element_by_css_selector("form#loginPopupform")
			form_mail = login_form.find_element_by_css_selector("input#loginFormUser_email")
			form_mail.send_keys(mail_str)
			form_pswd = login_form.find_element_by_css_selector("input#loginForm_password")
			form_pswd.send_keys(pswd_str)
			form_pswd.send_keys(Keys.RETURN)
			# form_btn = login_form.find_element_by_css_selector("a.newButton.orange")
			# form_btn.click()
			break
		except Exception as e:
			driver.save_screenshot('search_results.png') 
			print(e)
			close_btn = driver.find_element_by_css_selector("div.signupWrap.js-gen-popup.dark_graph > div.right > i.popupCloseIcon")
			close_btn.click()
			pass




if __name__ == '__main__': 
	main()
	# test_main()

