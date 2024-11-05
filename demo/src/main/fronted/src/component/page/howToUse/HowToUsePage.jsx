import React, { useState, useEffect } from "react";
import styled from "styled-components";
import step1 from "../../image/step1.png"
import step2 from "../../image/step2.png"
import step3 from "../../image/step3.png"
import step4 from "../../image/step4.png"

const steps = [
    { id: 1, title: 'Step 1: 바이낸스 API 키 생성', description:"", image: step1 },
    { id: 2, title: 'Step 2: 바이낸스에 CAT IP 등록', description: 'CAT IP : 3.35.65.112', image: step2 },
    { id: 3, title: 'Step 3: Future 계좌 생성', description: "", image: step3 },
    { id: 4, title: 'Step 4: 실행', description: '모든 설정이 완료되면 실행하세요.', image: step4 },
];

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
`;

const Image = styled.img`
  max-width: 70%; 
  height: auto; 
  margin-bottom: 20px;
`;

const Title = styled.h2`
  margin: 10px 0;
`;

const Description = styled.p`
    margin: 10px 0;
    font-size: 1.2rem;
`;

const NavigationButtons = styled.div`
    display: flex;
    justify-content: space-between;
    width: 80%;
    max-width: 300px;
    margin-top: 20px;
`;

const Button = styled.button`
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 5px;

    &:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
`;
function HowToUsePage() {
    const [currentStep, setCurrentStep] = useState(0);

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const { title, description, image } = steps[currentStep];

    return (
        <PageContainer>
            <Image src={process.env.PUBLIC_URL + image} alt={title} />
            <Title>{title}</Title>
            <Description>{description}</Description>
            <NavigationButtons>
                <Button onClick={handlePrev} disabled={currentStep === 0}>
                    이전
                </Button>
                <Button onClick={handleNext} disabled={currentStep === steps.length - 1}>
                    다음
                </Button>
            </NavigationButtons>
        </PageContainer>

    );
}

export default HowToUsePage;