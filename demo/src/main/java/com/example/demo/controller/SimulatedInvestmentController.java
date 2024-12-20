package com.example.demo.controller;
import com.example.demo.service.SimulatedInvestmentService;
import org.springframework.web.bind.annotation.*;
import com.example.demo.model.RequestName;
import com.example.demo.model.User;
import com.example.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

@RestController
@RequestMapping("/api/simulatedinvestments")
public class SimulatedInvestmentController {

    @Autowired
    private UserService userService;

    @PostMapping
    public void executePythonScript(@RequestBody RequestName request) {

        String username = request.getUsername();
        User user = userService.findByUsername(username);
        String strategy = request.getStrategy();
        String capital = request.getCapital();
        String orderSize = request.getOrderSize();
        String leverage = request.getLeverage();
        String profitStart = request.getProfitStart();
        String profitEnd = request.getProfitEnd();
        String lossStart = request.getLossStart();
        String lossEnd = request.getLossEnd();


        // MySQL 데이터베이스 연결 설정
        String dbuser = "root";
        String password = "Cat2024!!";
        String url = "jdbc:mysql://capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com:3306/backtest";

        try {
            // 데이터베이스 연결
            Connection connection = DriverManager.getConnection(url, dbuser, password);
            Statement statement = connection.createStatement();


            String updateFlagQuery = "UPDATE User SET " + strategy + "si = true WHERE username = '" + username + "'";
            statement.executeUpdate(updateFlagQuery);

            // 파이썬 스크립트 실행
            String pythonScriptPath = "/home/ec2-user/ttttt/python/" + strategy + "simtrade.py";
            ProcessBuilder processBuilder = new ProcessBuilder("python", pythonScriptPath, username, user.getApikey(), user.getApisecret(), capital, orderSize, leverage, profitStart, profitEnd, lossStart, lossEnd);
            Process process = processBuilder.start();

            // 실행 결과 출력
//            BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));
//            String line;
            System.out.println("파이썬 스크립트 실행 중: 모의투자 시작");
//            while ((line = stdoutReader.readLine()) != null) {
//                System.out.println(line);
//            }
//
//            // 실행 오류 출력
//            BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8));
//            System.err.println("파이썬 스크립트 실행 오류:");
//            while ((line = stderrReader.readLine()) != null) {
//                System.err.println(line);
//            }
//
//            // 종료 코드 확인
//            int exitCode = process.waitFor();
//            if (exitCode == 0) {
//                System.out.println("자동매매 종료");
//            } else {
//                System.err.println("Python 스크립트 실행 오류! 종료 코드: " + exitCode);
//            }

//            // 리더 닫기
//            stdoutReader.close();
//            stderrReader.close();

            // 데이터베이스 연결 및 리소스 닫기
            statement.close();
            connection.close();
        } catch (SQLException | IOException e) {
            System.err.println("Python 스크립트 실행 중 예외 발생: " + e.getMessage());
        }

    }

}
