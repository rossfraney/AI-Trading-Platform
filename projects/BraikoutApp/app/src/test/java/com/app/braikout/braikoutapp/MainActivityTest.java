package com.app.braikout.braikoutapp;

import android.support.test.rule.ActivityTestRule;
import android.view.View;

import org.json.JSONException;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import java.io.IOException;

public class MainActivityTest {

    @Test
    public void test_onCreate() throws IOException, JSONException {
        MainActivity mainActivity = new MainActivity();

        Assert.assertNotNull(mainActivity);
    }

    @Test
    public void test_postToken() throws IOException, JSONException {
        String token = "testoken1234";
        MainActivity.postToken(token);
        Assert.assertNotNull(token);

    }

    @Rule
    public ActivityTestRule<MainActivity> mainActivityActivityTestRule = new ActivityTestRule<>(MainActivity.class);
    private MainActivity mainActivity = null;

    @Before
    public void setUp() throws Exception{
        mainActivity = mainActivityActivityTestRule.getActivity();
    }

    @Test
    public void test_launch() throws IOException, JSONException {
        View view = mainActivity.findViewById(R.id.textView);

        Assert.assertNotNull(view);
    }

    @After
    public void tearDown() throws Exception{
        mainActivity = null;
    }

}