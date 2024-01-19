import puppeteer from "puppeteer";

const urls = [
  "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000142695&dispCatNo=100000200010015&trackingCd=Cat100000200010015_MID&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=1",
];

async function readOYoungPage(URL) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: "networkidle2" });
  await page.click(".goods_buyinfo");

  const prdDisplayName = await page.$(".prd_name");
  const prdBrand = await page.$(".prd_brand");
  const prdPrice = await page.$(".price-1");
  const prdSalePrice = await page.$(".price-2");

  const data = await page.evaluate(
    (name, brand, price, salePrice) => {
      return {
        prdDisplayName: name.textContent.replace(/\n|\t/g, "").trim(),
        prdBrand: brand.textContent.replace(/\n|\t/g, "").trim(),
        prdPrice: price.textContent.replace(/\n|\t|원/g, "").trim(),
        prdSalePrice: salePrice.textContent.replace(/\n|\t|원/g, "").trim(),
      };
    },
    prdDisplayName,
    prdBrand,
    prdPrice,
    prdSalePrice
  );
  const prdDetails = await getPrdDetails(page);

  await browser.close();
  return {
    ...data,
    prdDetails: prdDetails,
  };
}

async function getPrdDetails(page) {
  // const dtElements = await page.$$("#artcInfo dt");
  // const ddElements = await page.$$("#artcInfo dd");

  const detailsDict = await page.evaluate(() => {
    const dts = document.querySelectorAll("#artcInfo dt");
    const dds = document.querySelectorAll("#artcInfo dd");

    let results = {};
    for (let i = 0; i < dts.length; i++) {
      let key = dts[i].textContent.replace(/\n|\t/g, "").trim();
      let value = dds[i].textContent.replace(/\n|\t|(?<= ) +/g, "").trim();
      results[key] = value;
    }
    return results;
  });

  return detailsDict;
}

const data = await readOYoungPage(urls[0]);
console.log(data);
