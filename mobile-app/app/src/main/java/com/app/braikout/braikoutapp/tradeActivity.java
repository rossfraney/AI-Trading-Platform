package com.app.braikout.braikoutapp;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

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


public class tradeActivity extends AppCompatActivity {

    private static final String TAG = "TRADING" ;
    String orderType;
    static String feedback;
    static String feedbackType;
    Spinner type;
    EditText feedbackField;
    Spinner feedbackSpinner;

    public void sendFeedback(View button) {
        orderType = type.getSelectedItem().toString();

        feedback = feedbackField.getText().toString();

        feedbackType = feedbackSpinner.getSelectedItem().toString();
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    try {
                        postToken(feedback, feedbackType, orderType);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
        thread.start();
        Toast.makeText(this, "Order Placed. Return to Home Menu.", Toast.LENGTH_LONG).show();
        Log.d(TAG, orderType + feedback + feedbackType);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trade);
        type = findViewById(R.id.SpinnerFeedbackOrderType);
        feedbackField = findViewById(R.id.EditTextFeedbackBody);
        feedbackSpinner = findViewById(R.id.SpinnerFeedbackType);
    }

//    public static void postToken() throws IOException, JSONException {
//        URL url = null;
//        try {
//            url = new URL("https://d97rutwnvb.execute-api.us-east-2.amazonaws.com/orders/orders");
//            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
//            connection.setConnectTimeout(5000);//5 secs
//            connection.setReadTimeout(5000);//5 secs
//
//            connection.setRequestMethod("POST");
//            connection.setDoOutput(true);
//            connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
//
//            JSONObject cred = new JSONObject();
//
//            cred.put("coin_id",feedbackType);
//            cred.put("type", "buy");
//            cred.put("amt", feedback);
//
//            OutputStreamWriter out = new OutputStreamWriter(connection.getOutputStream());
//            out.write(cred.toString());
//            out.flush();
//            out.close();
//
//            int res = connection.getResponseCode();
//
//            System.out.println(res);
//
//
//            InputStream is = connection.getInputStream();
//            BufferedReader br = new BufferedReader(new InputStreamReader(is));
//            String line = null;
//            while((line = br.readLine() ) != null) {
//                Log.d(TAG, line);
//            }
//            connection.disconnect();
//        } catch (MalformedURLException e) {
//            e.printStackTrace();
//        }
//    }
public static void postToken(String amt, String coin, String type) throws IOException, JSONException {
    URL url = null;
    try {
        url = new URL("https://d97rutwnvb.execute-api.us-east-2.amazonaws.com/orders");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setConnectTimeout(5000);//5 secs
        connection.setReadTimeout(5000);//5 secs

        connection.setRequestMethod("POST");
        connection.setDoOutput(true);
        connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");

        JSONObject cred = new JSONObject();

        cred.put("coin_id", coin.toLowerCase());
        cred.put("type", type);
        cred.put("amt", amt);

        OutputStreamWriter out = new OutputStreamWriter(connection.getOutputStream());
        out.write(cred.toString());
        out.flush();
        out.close();

        int res = connection.getResponseCode();

        System.out.println(res);


        InputStream is = connection.getInputStream();
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        String line = null;
        while((line = br.readLine() ) != null) {
            Log.d(TAG, line);
        }
        connection.disconnect();
    } catch (MalformedURLException e) {
        e.printStackTrace();
    }
}

}
