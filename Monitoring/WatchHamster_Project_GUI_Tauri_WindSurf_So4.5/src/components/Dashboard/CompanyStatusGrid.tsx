/**
 * 회사별 현황 그리드 컴포넌트
 * 모든 회사의 상태를 카드 형식으로 표시
 */

import React from 'react';
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Button,
  HStack,
  Spacer,
  useColorModeValue
} from '@chakra-ui/react';
import { FiPlus } from 'react-icons/fi';
import CompanyStatusCard from './CompanyStatusCard';

interface CompanySummary {
  id: string;
  name: string;
  display_name: string;
  is_active: boolean;
  webhook_count: number;
  total_sent: number;
  success_rate: number;
  last_activity: string;
  news_monitors: number;
  news_status: string;
}

interface CompanyStatusGridProps {
  companies: CompanySummary[];
  onCompanyClick: (companyId: string) => void;
  onAddCompany?: () => void;
  isLoading?: boolean;
}

export const CompanyStatusGrid: React.FC<CompanyStatusGridProps> = ({
  companies,
  onCompanyClick,
  onAddCompany,
  isLoading = false
}) => {
  const headingColor = useColorModeValue('gray.700', 'white');

  return (
    <Box>
      <HStack mb={4}>
        <Heading size="md" color={headingColor}>
          🏢 회사별 현황 ({companies.length}개)
        </Heading>
        <Spacer />
        {onAddCompany && (
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            size="sm"
            onClick={onAddCompany}
          >
            회사 추가
          </Button>
        )}
      </HStack>

      {companies.length === 0 ? (
        <Box
          p={8}
          textAlign="center"
          borderWidth="2px"
          borderStyle="dashed"
          borderRadius="lg"
          borderColor="gray.300"
        >
          <Text color="gray.500" mb={4}>
            등록된 회사가 없습니다
          </Text>
          {onAddCompany && (
            <Button
              leftIcon={<FiPlus />}
              colorScheme="blue"
              onClick={onAddCompany}
            >
              첫 회사 추가하기
            </Button>
          )}
        </Box>
      ) : (
        <Grid
          templateColumns="repeat(auto-fill, minmax(300px, 1fr))"
          gap={4}
        >
          {companies.map((company) => (
            <GridItem key={company.id}>
              <CompanyStatusCard
                company={company}
                onClick={() => onCompanyClick(company.id)}
              />
            </GridItem>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default CompanyStatusGrid;
