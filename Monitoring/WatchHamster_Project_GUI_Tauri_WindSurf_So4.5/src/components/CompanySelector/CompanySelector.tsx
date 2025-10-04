import React, { useState, useEffect } from 'react';
import {
  Box,
  Select,
  Flex,
  Text,
  Avatar,
  Badge,
  useColorModeValue
} from '@chakra-ui/react';

interface Company {
  id: string;
  name: string;
  display_name: string;
  logo_url?: string;
  is_active: boolean;
}

interface CompanySelectorProps {
  selectedCompanyId?: string;
  onCompanyChange: (companyId: string) => void;
  showLabel?: boolean;
}

export const CompanySelector: React.FC<CompanySelectorProps> = ({
  selectedCompanyId,
  onCompanyChange,
  showLabel = true
}) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/companies?active_only=true');
      const data = await res.json();
      setCompanies(data);
      
      // 선택된 회사가 없으면 첫 번째 회사 자동 선택
      if (!selectedCompanyId && data.length > 0) {
        onCompanyChange(data[0].id);
      }
    } catch (err) {
      console.error('회사 목록 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedCompany = companies.find(c => c.id === selectedCompanyId);

  return (
    <Box>
      {showLabel && (
        <Text fontSize="sm" fontWeight="bold" mb={2} color="gray.600">
          회사 선택
        </Text>
      )}
      
      <Flex align="center" gap={3}>
        {selectedCompany?.logo_url && (
          <Avatar 
            size="sm" 
            src={selectedCompany.logo_url} 
            name={selectedCompany.name}
          />
        )}
        
        <Select
          value={selectedCompanyId || ''}
          onChange={(e) => onCompanyChange(e.target.value)}
          isDisabled={loading}
          bg={bgColor}
          borderColor={borderColor}
          size="md"
          fontWeight="bold"
        >
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.display_name} ({company.name})
            </option>
          ))}
        </Select>
        
        {selectedCompany && (
          <Badge colorScheme="green" fontSize="xs">
            활성
          </Badge>
        )}
      </Flex>
    </Box>
  );
};

export default CompanySelector;
