use reqwest::blocking::Client;

fn main() {
    println!("Time to ask Kraken a question!");
    let url = "https://api.kraken.com/0/public/OHLC?pair=ETHEUR";
    let client: Client = Client::new();
    // TODO: do not use unwrap().
    // TODO: now it's a string instead of a JSON, but the response is a JSON.
    let resp = client
        .get(url)
        .send()
        .unwrap()
        .text();
    print!("Response code: {:?}", resp);
}
