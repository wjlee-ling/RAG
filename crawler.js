import puppeteer from "puppeteer";

const urls = [
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000142695&dispCatNo=100000200010015&trackingCd=Cat100000200010015_MID&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=1",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000164736&dispCatNo=100000200010015&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=2",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000189370&dispCatNo=100000200010015&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=3",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000112149&dispCatNo=100000200010015&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=5",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000151410&dispCatNo=100000200010015&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%B9%84%ED%83%80%EB%AF%BC_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=9",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000167747&dispCatNo=100000200010024&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%9C%A0%EC%82%B0%EA%B7%A0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=1",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000186204&dispCatNo=100000200010024&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%9C%A0%EC%82%B0%EA%B7%A0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=4",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000179239&dispCatNo=100000200010024&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%9C%A0%EC%82%B0%EA%B7%A0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=17",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000189360&dispCatNo=100000200010024&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%9C%A0%EC%82%B0%EA%B7%A0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=12",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000188377&dispCatNo=100000200010024&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%9C%A0%EC%82%B0%EA%B7%A0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=6",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000175634&dispCatNo=100000200010023&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%8A%AC%EB%A6%AC%EB%B0%8D/%EC%9D%B4%EB%84%88%EB%B7%B0%ED%8B%B0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=1",
  "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000186305&dispCatNo=100000200010023&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%8A%AC%EB%A6%AC%EB%B0%8D/%EC%9D%B4%EB%84%88%EB%B7%B0%ED%8B%B0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=2",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000191318&dispCatNo=100000200010023&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%8A%AC%EB%A6%AC%EB%B0%8D/%EC%9D%B4%EB%84%88%EB%B7%B0%ED%8B%B0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=3",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000186264&dispCatNo=100000200010023&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%8A%AC%EB%A6%AC%EB%B0%8D/%EC%9D%B4%EB%84%88%EB%B7%B0%ED%8B%B0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=9",
  // "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000185637&dispCatNo=100000200010023&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%8A%AC%EB%A6%AC%EB%B0%8D/%EC%9D%B4%EB%84%88%EB%B7%B0%ED%8B%B0_%EC%A0%84%EC%B2%B4__%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=16",
];

async function readOYoungPage(URL) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: "networkidle2" });
  await page.waitForSelector("a.goods_buyinfo");
  await page.click("a.goods_buyinfo");

  const prdDisplayName = await page.$(".prd_name");
  const prdBrand = await page.$(".prd_brand");
  const prdPrice = await page.$(".price-1"); // 세일 안하면 element 없음
  const prdSalePrice = await page.$(".price-2"); // 최종 가격

  const data = await page.evaluate(
    (name, brand, price, salePrice) => {
      return {
        prdDisplayName: name.textContent.replace(/\n|\t/g, "").trim(),
        prdBrand: brand.textContent.replace(/\n|\t/g, "").trim(),
        prdPrice: price
          ? price.textContent.replace(/\n|\t|원/g, "").trim()
          : null,
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
  await page.waitForSelector("#artcInfo dt");

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

for (let i = 0; i < urls.length; i++) {
  const data = await readOYoungPage(urls[i]);
  console.log(data);
}
