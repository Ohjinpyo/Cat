package com.example.demo.controller;

import com.example.demo.model.BackTestResult;
import org.json.JSONObject;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
public class BackTestController {

    @PostMapping("/api/test")
    public BackTestResult getBackTestResult(@RequestBody Map<String, String> dates) {
        String startDate = dates.get("startDate");
        String endDate = dates.get("endDate");
        String capital = dates.get("capital");
        String orderSize = dates.get("orderSize");
        String leverage = dates.get("leverage");


        System.out.print(startDate);
        System.out.println(endDate);

        BackTestResult backTestResult = new BackTestResult();

        try {
            String scriptPath = "/home/ec2-user/ttttt/devide_bakctest2.py";


            // Python 스크립트를 실행
            ProcessBuilder pb = new ProcessBuilder("python", scriptPath, startDate, endDate, capital, orderSize, leverage);
            Process process = pb.start();

            // 실행 결과를 읽어오기 위한 버퍼 리더 생성
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));

            // 실행 결과를 문자열로 저장
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            // 프로세스 종료까지 대기
            process.waitFor();

            // JSON 파싱
            JSONObject jsonObject = new JSONObject(output.toString());

            // 결과를 BackTestResult 객체에 설정
            backTestResult.setStartdate(jsonObject.getString("start"));
            backTestResult.setEnddate(jsonObject.getString("end"));
            backTestResult.setDeposit(jsonObject.getString("capital"));
            backTestResult.setProfit(jsonObject.getString("profit"));
            backTestResult.setCounts(jsonObject.getString("trade_count"));
            backTestResult.setWinrate(jsonObject.getString("winrate"));

        } catch (Exception e) {
            e.printStackTrace();
            // 오류가 발생한 경우 기본 값을 설정하거나 에러 처리를 합니다.
            backTestResult.setStartdate(startDate);
            backTestResult.setEnddate(endDate);
            backTestResult.setDeposit("Error");
            backTestResult.setProfit("Error");
            backTestResult.setCounts("Error");
            backTestResult.setWinrate("Error");

        }

        return backTestResult;
    }
}
