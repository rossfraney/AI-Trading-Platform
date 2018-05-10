package com.app.braikout.braikoutapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.google.firebase.iid.FirebaseInstanceId;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import static com.amazonaws.http.HttpHeader.USER_AGENT;

public class MainActivity extends AppCompatActivity implements View.OnClickListener{
    private Button openButton;
    private Button logoutButton;
    public String token;
    private static final String TAG = "MainActivity";
    private List<String> wallets;
//    private String bucket;
//    private String key;
//    private long bytesTotal;
//    private long bytesTransferred;
//    private TransferState transferState;
//    private String filePath;

//    private TransferListener transferListener;
//    File fileToUpload = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath() + "/token.txt");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        openButton = findViewById(R.id.trade);
        openButton.setOnClickListener(this);

        logoutButton = findViewById(R.id.logout);
        logoutButton.setOnClickListener(this);

        token = FirebaseInstanceId.getInstance().getToken();
        Log.d(TAG, "TOKEN = " + token);

        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    try {
                        postToken(token);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
        thread.start();

        Thread thread2 = new Thread(new Runnable() {
            @Override
            public void run() {
                wallets = new ArrayList<>();
                String [] coins = {"btc", "ltc", "eth", "eur", "usd"};
                for(String coin : coins){
                    try{
                        URL obj = new URL("https://xwkylkf6v4.execute-api.us-east-2.amazonaws.com/alerts/coin_id/"+coin);
                        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
                        con.setRequestMethod("GET");
                        con.setRequestProperty("User-Agent", USER_AGENT);
                        int responseCode = con.getResponseCode();
                        if (responseCode == HttpURLConnection.HTTP_OK) { // success
                            BufferedReader in = new BufferedReader(new InputStreamReader(
                                    con.getInputStream()));
                            String inputLine;
                            StringBuilder response = new StringBuilder();

                            while ((inputLine = in.readLine()) != null) {
                                response.append(inputLine);
                            }
                            in.close();

                            // print result
                            wallets.add(response.toString());
                        } else {
                            System.out.println("GET request not worked");
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        });
        thread2.start();
        try {
            thread2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        List<String> js = new ArrayList<>();
        for(String s: wallets){
            String coinid = s.split(":")[6].split("")[2] +s.split(":")[6].split("")[3] + s.split(":")[6].split("")[4];
            String amt = s.split(":")[4].split("")[2] + s.split(":")[4].split("")[3] + s.split(":")[4].split("")[4] + s.split(":")[4].split("")[5];
            amt = amt.replace('"', ' ');

            js.add(coinid + " : " + amt);
        }

        StringBuilder sb = new StringBuilder();
        for(String s: js){
            sb.append(s + "\n");
        }

        TextView mText = findViewById(R.id.wallet);
        mText.setText(sb.toString());
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onClick(View view) {
        if (view == openButton) {
            openTradeOptions(); //if user hits the open button
        }

        if (view == logoutButton) {
            logOut(); //if user hits the open button
        }
        //Changes neighbour's number variable and pre-creates the text message
    }

    private void logOut() {
        final Intent logout = new Intent(MainActivity.this, LoggedOut.class);
        startActivity(logout);
    }

    public void openTradeOptions() {
        final Intent trade = new Intent(MainActivity.this, tradeActivity.class);
        startActivity(trade);
    }

    public static void postToken(String token) throws IOException, JSONException {
        URL url = null;
        try {
            url = new URL("https://xwkylkf6v4.execute-api.us-east-2.amazonaws.com/alerts/coins");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000);//5 secs
            connection.setReadTimeout(5000);//5 secs

            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");

            JSONObject cred = new JSONObject();

            cred.put("coin_id","tokenId");
            cred.put("token", token);

            OutputStreamWriter out = new OutputStreamWriter(connection.getOutputStream());
            out.write(cred.toString());
            out.flush();
            out.close();

            int res = connection.getResponseCode();

            System.out.println(res);
            Log.d(TAG, String.valueOf(res));

            InputStream is = connection.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(is));
            String line = null;
            while((line = br.readLine() ) != null) {
                Log.d(TAG, line);
            }
            connection.disconnect();
        } catch (MalformedURLException e) {
            Log.d(TAG, String.valueOf(e));
            e.printStackTrace();
        }
    }
}
